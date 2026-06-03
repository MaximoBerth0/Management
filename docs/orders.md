# Orders Module

Manages the order lifecycle: creating an order, adding/removing line items while it is still a draft, and driving it through its state transitions (`confirm` → `complete`, or `cancel`). The order itself owns no stock logic — reserving, releasing, and fulfilling inventory is delegated to the `inventory` module, with the order service orchestrating both sides inside a single transaction.

---

## Architecture Overview

```
┌──────────┐  1:N   ┌──────────────┐  1:1   ┌──────────────────┐
│  Order   │───────▶│  OrderItem   │───────▶│ StockReservation │
│ (status) │        │ (product+qty)│ opt.   │  (inventory mod) │
└──────────┘        └──────────────┘        └──────────────────┘
```

**Core principle:** the `Order` is a small state machine. Item edits are only allowed while `CREATED`; once confirmed, the order's items are mirrored as `StockReservation`s in the inventory module. State transitions that touch inventory (`confirm`, `cancel`, `complete`) are wrapped in a service-owned transaction so the order row and the reservation rows commit (or roll back) together.

### Order State Machine

```
        add/remove items
        ┌───────────┐
        ▼           │
   ┌─────────┐  confirm   ┌───────────┐  complete   ┌───────────┐
   │ CREATED │───────────▶│ CONFIRMED │────────────▶│ COMPLETED │
   └────┬────┘            └─────┬─────┘             └───────────┘
        │                       │
        │ cancel                │ cancel
        ▼                       ▼
   ┌───────────┐          ┌───────────┐
   │ CANCELLED │◀─────────│ CANCELLED │
   └───────────┘          └───────────┘
```

`COMPLETED` and `CANCELLED` are terminal. Items can only be mutated in `CREATED`.

---

## Model

[app/orders/models/order.py](../app/orders/models/order.py)

### Order
| Field | Notes |
|---|---|
| `user_id` | FK → `users.id`, indexed — the order owner |
| `status` | `OrderStatus` enum, the state-machine state |
| `created_at`, `updated_at` | `updated_at` bumped via `onupdate` on every change |
| `items` | 1:N to `OrderItem`, `cascade="all, delete-orphan"` |

The model carries the transition guards as methods — `confirm`, `cancel`, `complete`, `add_item`, `remove_item` — each raising a typed domain exception (`InvalidOrderStatus`, `OrderItemNotFound`) if called from an illegal state. `add_item`/`remove_item` are rejected unless the order is `CREATED`.

### OrderItem
| Field | Notes |
|---|---|
| `order_id`, `product_id` | FKs, both indexed |
| `quantity` | Validated `> 0` at `OrderItem.create` |
| `reservation` | Optional 1:1 backref to `StockReservation` (cross-module) — set when the order is confirmed |

### OrderStatus — [models/enums.py](../app/orders/models/enums.py)
`CREATED` · `CONFIRMED` · `CANCELLED` · `COMPLETED` (string enum).

---

## Schemas

[app/orders/schemas.py](../app/orders/schemas.py)

Single-file schemas. Response models use `ORMModel` (`from_attributes=True`) to read straight off ORM objects.

| Request | Response |
|---|---|
| `AddItemRequest` (`product_id`, `quantity` — both `> 0`) | `OrderResponse` |
| `ConfirmOrderRequest` (`location_id` — `> 0`) | `OrderItemResponse` |

`OrderResponse` nests the line items as `List[OrderItemResponse]` (defaults to `[]`).

---

## Repository

[app/orders/repository.py](../app/orders/repository.py)

Pure data access — no business logic, no status validation (that lives on the model/service).

| Method | Notes |
|---|---|
| `get_order` | Eager-loads `items` and each item's `reservation` via chained `selectinload` to avoid N+1 across the order→item→reservation chain |
| `create_order` | Builds via `Order.create`, adds, commits, refreshes |
| `append_item` | Loads the order (returns `None` if missing), delegates to `order.add_item`, commits, refreshes `items` |
| `remove_item` | Loads the order (returns `None` if missing), delegates to `order.remove_item`, commits |

`get_order` is the single read path used by every state transition, so the reservation chain is always available without extra queries.

---

## Service

[app/orders/service.py](../app/orders/service.py)

Business logic layer. Routers never call the repository directly. The constructor takes the `AsyncSession`, an `OrderRepository`, and the cross-module `InventoryService`.

Key decisions:

- **`create_order`**: thin wrapper over the repository — creates a `CREATED` order for the given user.
- **`add_item_to_order` / `remove_item_from_order`**: delegate to the repository; raise `OrderNotFound` when the order is missing. Item-state rules (only on `CREATED`) are enforced by the model.
- **Transaction ownership:** `confirm_order`, `cancel_order`, and `complete_order` open `async with self.db.begin()` because each spans both order state **and** inventory reservations. If any inventory call fails, the whole operation rolls back — the order never ends up half-transitioned.
  - **`confirm_order`**: requires `CREATED`, else `InvalidOrderStatus`. Reserves stock for every line item via `inventory_service.reserve_for_item`, then flips status to `CONFIRMED`.
  - **`cancel_order`**: requires `CONFIRMED`, else `InvalidOrderStatus`. Releases each item's reservation (`release_for_item`) before `order.cancel()`.
  - **`complete_order`**: fulfills each item's reservation (`fulfill_for_item`), then `order.complete()` — which guards `CONFIRMED` → `COMPLETED`, raising `InvalidOrderStatus` (409) otherwise.

All not-found and invalid-status branches emit `logger.warning` with `order_id`; successful transitions emit `logger.info`. The router logs a paired `"<endpoint> endpoint called"` / `"… succeeded"` around each call.

---

## Dependencies

[app/orders/dependencies.py](../app/orders/dependencies.py)

Single dependency — `get_order_service` — that injects an `AsyncSession`, builds an `OrderRepository`, and pulls in the shared `InventoryService` (via `provide_inventory_service`), wiring all three into an `OrderService`.

---

## Routers

[app/orders/router.py](../app/orders/router.py)

Thin HTTP layer under the `/orders` prefix. Calls the service and returns the result; domain errors propagate to the global `AppError` handler. Every route requires a permission via `require_permission`; `POST /orders` additionally injects `get_current_user` to record the owner.

| Endpoint | Permission |
|---|---|
| `POST /orders` | `order:create` |
| `POST /orders/{id}/items` | `order:add` |
| `DELETE /orders/{order_id}/items/{product_id}` | `order:remove` |
| `PATCH /orders/{id}/confirm` | `order:confirm` |
| `PATCH /orders/{id}/cancel` | `order:cancel` |
| `PATCH /orders/{id}/complete` | `order:complete` |

---

## Errors

[app/orders/exceptions.py](../app/orders/exceptions.py)

Domain-specific exceptions extending the shared `AppError` base (via the module's `OrderError`). Each carries a typed `error_code` for machine-readable handling on the client.

| Exception | HTTP | Code |
|---|---|---|
| `OrderError` (base) | 400 | `ORDER_ERROR` |
| `OrderNotFound` | 404 | `ORDER_NOT_FOUND` |
| `InvalidOrderStatus` | 409 | `INVALID_ORDER_STATUS` |
| `OrderItemNotFound` | 404 | `ORDER_ITEM_NOT_FOUND` |
| `InvalidQuantity` | 422 | `INVALID_QUANTITY` |

The model's transition guards (`confirm`, `cancel`, `complete`, `add_item`, `remove_item`) and `OrderItem.create` raise these typed exceptions directly — never raw `ValueError`s — so illegal state transitions and bad quantities surface as proper 409/422/404 responses through the global `AppError` handler.

---

## Flow Diagram — Confirm Order

```
PATCH /orders/{id}/confirm
      │  (payload: location_id)
      ▼
┌──────────────────────────────┐
│ require_permission           │
│   (order:confirm)            │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ async with db.begin():       │ ← service owns the transaction
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ get_order(id)                │ ← OrderNotFound (404) if missing
│ status == CREATED?           │ ← InvalidOrderStatus (409) if not
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ for item in order.items:     │
│   inventory.reserve_for_item │ ← reserves stock per line item
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ order.status = CONFIRMED     │ ← commit on context exit
└──────────────┬───────────────┘   (rolls back if any reserve fails)
               ▼
          OrderResponse
```

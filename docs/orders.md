# Orders Module

Manages the order lifecycle: creating an order, adding/removing line items while it is still a draft, and driving it through its state transitions (`confirm` → `complete`, or `cancel`). The order itself owns no stock logic — reserving, releasing, and fulfilling inventory is delegated to the `inventory` module, with the order service orchestrating both sides inside a single transaction.

Each order also carries a short, human-typable **lookup code** (`XXXX-XXXX`) so a customer can retrieve their order through a single **public, unauthenticated** endpoint without an account — the code itself acts as the credential.

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
| `code` | `XXXX-XXXX` lookup code — `unique`, indexed, `nullable=False`. The public read credential |
| `user_id` | FK → `users.id`, indexed — the order owner (the staff member who created it) |
| `status` | `OrderStatus` enum, the state-machine state |
| `created_at`, `updated_at` | `updated_at` bumped via `onupdate` on every change |
| `items` | 1:N to `OrderItem`, `cascade="all, delete-orphan"` |

**Code generation** — `generate_order_code()` draws 8 characters from a Crockford-style base32 alphabet (`0-9A-Z`, omitting the ambiguous `I L O U`) via `secrets.choice`, formatted as `XXXX-XXXX`. `Order.create` assigns it at construction; collisions against the `unique` constraint are handled by the repository (see below).

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
| `AddItemRequest` (`product_id`, `quantity` — `gt=0`) | `OrderResponse` (`id`, `user_id`, `status`, timestamps, `items`) |
| | `OrderItemResponse` (`id`, `product_id`, `quantity`, `created_at`) |

`OrderResponse` nests the line items as `List[OrderItemResponse]` (defaults to `[]`).

**Note:** `OrderResponse` deliberately does **not** expose `code`. The code is an inbound credential customers already hold; it's never echoed back in API responses (nor written to logs).

---

## Repository

[app/orders/repository.py](../app/orders/repository.py)

Pure data access — no business logic, no status validation (that lives on the model/service).

| Method | Notes |
|---|---|
| `get_order` | Eager-loads `items` and each item's `reservation` via chained `selectinload` to avoid N+1 across the order→item→reservation chain |
| `get_order_by_code` | Same eager-loading as `get_order`, keyed on the unique `code`; returns `Order | None` |
| `list_orders_by_user` | All of a user's orders, newest first, with the same eager-loaded chain |
| `create_order` | Builds via `Order.create` and commits; on the unique-`code` `IntegrityError` it rolls back and retries (up to `_MAX_CODE_RETRIES = 5`), raising `OrderCodeGenerationError` if every attempt collides |
| `append_item` | Loads the order (returns `None` if missing), delegates to `order.add_item`, commits, refreshes `items` |
| `remove_item` | Loads the order (returns `None` if missing), delegates to `order.remove_item`, commits |

`get_order` is the single read path used by every state transition, so the reservation chain is always available without extra queries. `get_order_by_code` is the read path for the public lookup endpoint.

---

## Service

[app/orders/service.py](../app/orders/service.py)

Business logic layer. Routers never call the repository directly. The constructor takes the `AsyncSession`, an `OrderRepository`, and the cross-module `InventoryService`.

Key decisions:

- **`create_order`**: thin wrapper over the repository — creates a `CREATED` order (with a generated `code`) for the given user.
- **`list_user_orders`**: returns the caller's own orders via the repository; backs the authenticated `GET /orders/me`.
- **`get_order_by_code`**: backs the public lookup. Normalizes the caller-supplied code with the module-level `_normalize_code` helper (upper-cases, strips whitespace, drops the dash, re-inserts it at the canonical position) so `abcd1234`, `ABCD-1234`, and ` ABCD 1234 ` all resolve to the stored form. Both failure modes — a malformed code (rejected before any DB hit) **and** a well-formed code with no match — raise the same `OrderNotFound` (404), so the public endpoint never reveals which codes are well-formed.
- **`add_item_to_order` / `remove_item_from_order`**: delegate to the repository; raise `OrderNotFound` when the order is missing. Item-state rules (only on `CREATED`) are enforced by the model.
- **Transaction ownership:** `confirm_order`, `cancel_order`, and `complete_order` span both order state **and** inventory reservations, then `await self.db.commit()` once at the end so the order row and reservation rows persist together; an exception from any inventory call propagates before the commit, leaving the order un-transitioned.
  - **`confirm_order`**: requires `CREATED`, else `InvalidOrderStatus`. Reserves stock for every line item via `inventory_service.reserve_for_item`, then flips status to `CONFIRMED`.
  - **`cancel_order`**: requires `CONFIRMED`, else `InvalidOrderStatus`. Releases each item's reservation (`release_for_item`) before `order.cancel()`.
  - **`complete_order`**: fulfills each item's reservation (`fulfill_for_item`), then `order.complete()` — which guards `CONFIRMED` → `COMPLETED`, raising `InvalidOrderStatus` (409) otherwise.

All not-found and invalid-status branches emit `logger.warning` with `order_id`; successful transitions emit `logger.info`. The router logs a paired `"<endpoint> endpoint called"` / `"… succeeded"` around each call. The lookup path logs neither the raw nor normalized code.

---

## Dependencies

[app/orders/dependencies.py](../app/orders/dependencies.py)

Single dependency — `get_order_service` — that injects an `AsyncSession`, builds an `OrderRepository`, and pulls in the shared `InventoryService` (via `provide_inventory_service`), wiring all three into an `OrderService`.

---

## Routers

[app/orders/router.py](../app/orders/router.py)

Thin HTTP layer under the `/orders` prefix. Calls the service and returns the result; domain errors propagate to the global `AppError` handler. Auth varies by route — most write/transition routes require a permission via `require_permission`, but two reads are looser: `GET /orders/me` only requires authentication (self-scoped), and `GET /orders/code/{code}` is fully public.

| Endpoint | Auth |
|---|---|
| `GET /orders/code/{code}` | **None — public.** The code is the credential |
| `GET /orders/me` | Authenticated only (`get_current_user`), no permission — returns the caller's own orders |
| `POST /orders` | `order:create` (+ `get_current_user` to record the owner) |
| `POST /orders/{id}/items` | `order:add` |
| `DELETE /orders/{order_id}/items/{product_id}` | `order:remove` |
| `PATCH /orders/{id}/confirm` | `order:confirm` (+ `get_current_location` from the `X-Location-Id` header) |
| `PATCH /orders/{id}/cancel` | `order:cancel` |
| `PATCH /orders/{id}/complete` | `order:complete` |

`GET /orders/code/{code}` uses a `/code/` literal segment so its `str` path param never collides with the UUID-typed `/{id}` routes. Because it's unauthenticated and the keyspace is guessable (32⁸ ≈ 1.1 × 10¹²), it's the natural candidate for rate-limiting if/when that middleware is added.

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
| `OrderCodeGenerationError` | 500 | `ORDER_GENERATION_CODE_FAILED` |

`OrderCodeGenerationError` is raised only if the repository exhausts its retry budget without finding a free `code` — a practically unreachable case given the keyspace, surfaced as a 500 rather than silently looping.

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
│ get_current_location         │ ← from X-Location-Id header
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
└──────────────┬───────────────┘   (exception here → no commit)
               ▼
┌──────────────────────────────┐
│ order.status = CONFIRMED     │
│ await db.commit()            │ ← order + reservations persist together
└──────────────┬───────────────┘
               ▼
          OrderResponse
```

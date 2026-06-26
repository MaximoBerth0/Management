# Inventory Module

Manages products, categories, physical locations, and per-location stock with a full audit trail of every quantity change. Stock movements are append-only — quantity adjustments always produce a `StockMovement` record alongside the updated `InventoryStock` row.

---

## Architecture Overview
```
┌──────────┐  M:N   ┌────────────┐
│ Products │◀──────▶│ Categories │
└────┬─────┘        └────────────┘
     │ 1:N
     ▼
┌──────────────────┐   1:N    ┌──────────────────┐
│ InventoryStock   │─────────▶│  StockMovement   │
│ (product+location│  audit   │ (IN/OUT/ADJUST)  │
│  qty + reserved) │          └──────────────────┘
└────────┬─────────┘
         │ 1:N         ┌────────────────────────┐   1:1   ┌──────────────┐
         ├────────────▶│   StockReservation     │────────▶│  OrderItem   │
         │             │ (RESERVED/FULFILLED/…) │  uniq   │ (orders mod) │
         │ N:1         └────────────────────────┘         └──────────────┘
         ▼
   ┌────────────┐
   │  Location  │
   └────────────┘
```

**Core principle:** `InventoryStock` is the only mutable quantity. Every change to `stock.quantity` is paired with an immutable `StockMovement` capturing `previous_quantity`, `new_quantity`, `movement_type`, and `created_by`. A second axis — `reserved_quantity` — is driven by the orders module through `StockReservation`s: confirming an order reserves stock (raising `reserved_quantity`), and completing it converts the reservation into an actual outflow.

---

## Models

[app/inventory/models/](../app/inventory/models/)

### Product — [product.py](../app/inventory/models/product.py)
| Field | Notes |
|---|---|
| `sku` | Unique, indexed — normalized to uppercase by the service |
| `is_active` | Soft delete flag — `DELETE /products/{id}` flips this, not a hard delete |
| `categories` | Many-to-many via `inventory_product_categories` |
| `stocks` | `cascade="all, delete-orphan"` — stock rows die with the product |
| `reservations` | Backref from `orders.StockReservation` (cross-module) |

### Category — [category.py](../app/inventory/models/category.py)
| Field | Notes |
|---|---|
| `name`, `description` | No unique constraint at DB level — uniqueness enforced in the service |
| `products` | Many-to-many backref |

### Location — [location.py](../app/inventory/models/location.py)
Model: `id`, `name`, `city`, `address`, plus a backref to its stocks. Locations have a full CRUD API (list, get, create, update, delete). `name` is treated as a logical unique key. A location that still has `InventoryStock` rows cannot be deleted (`LocationHasStock`, 409).

### InventoryStock — [stock.py](../app/inventory/models/stock.py)
| Field | Notes |
|---|---|
| `location_id`, `product_id` | FKs; the pair is treated as a logical unique key (looked up via `get_stock_by_location_and_product`) |
| `quantity` | Current on-hand quantity |
| `reserved_quantity` | Held by open reservations; managed only by the reservation methods, never by `in/out/adjust`. Available-to-promise = `quantity - reserved_quantity` |
| `reorder_point` | Restock threshold captured at creation; surfaced in stock-level responses |

### StockMovement — [stock.py](../app/inventory/models/stock.py)
Append-only audit row. Carries `movement_type` (`IN` / `OUT` / `ADJUST`), the delta `quantity`, both `previous_quantity` and `new_quantity`, and `created_by` (FK → `users.id`). For `ADJUST`, `quantity` stores the absolute difference between the new and old value.

### StockReservation — [reservation.py](../app/inventory/models/reservation.py)
Bridges an order line to the stock it holds (table `stock_reservation`).
| Field | Notes |
|---|---|
| `order_item_id` | FK → `order_items.id`, **unique** — one reservation per line item (1:1) |
| `stock_id` | FK → `inventory_stock.id`, indexed |
| `quantity` | Units held |
| `status` | `ReservationStatus` — `RESERVED` → `FULFILLED` or `RELEASED` (plus `FAILED`) |

`StockReservation.create` guards `quantity > 0` and starts the row in `RESERVED`.

### Enums — [models/enums.py](../app/inventory/models/enums.py)
`StockMovementType` (`IN` / `OUT` / `ADJUST`) and `ReservationStatus` (`RESERVED` / `FULFILLED` / `RELEASED` / `FAILED`), both string enums.

---

## Schemas

[app/inventory/schemas.py](../app/inventory/schemas.py)

Single-file schemas. Request models validate input length/range; response models use `ORMModel` (`from_attributes=True`) to read straight off ORM objects.

| Request | Response |
|---|---|
| `ProductCreate`, `ProductUpdate` | `ProductResponse`, `ProductListItemResponse` |
| `CategoryCreate`, `AddProductToCategory`, `RemoveProducFromCategory` | `CategoryResponse` |
| `StockInitialize`, `StockTransaction` | `StockResponse`, `StockListResponse` |
|  | `StockMovementResponse`, `StockMovementListResponse` |

`StockTransaction` is the shared payload for `stock:in` / `stock:out` / `stock:adjust` — same shape, different semantics in the service.

---

## Repositories

[app/inventory/repositories/](../app/inventory/repositories/)

Each repository wraps an `AsyncSession` and does pure data access — no validation, no normalization.

### ProductRepository
`get_product`, `get_by_sku`, `list_products`, `create_product`, `update_product` (partial — only updates non-None fields), `activate_product` / `deactivate_product` (flip `is_active`), `save`, `add_category` / `remove_category` (mutates the M:N collection in-memory then commits).

### CategoryRepository
`get_category`, `get_by_name`, `list_categories`, `create_category`, `save_category`, `remove_product` (removes a product from `category.products`), `delete_category` (hard delete).

### LocationRepository
`get_location`, `list_locations`, `get_by_name`, `create_location`, `update_location`, `delete_location`. `StockRepository.location_has_stock` backs the delete guard.

### StockRepository
| Method | Notes |
|---|---|
| `get_stock` | Lookup by stock id |
| `get_stock_by_location_and_product` | Lookup by the logical (location, product) key — the entry point for every `in/out/adjust` |
| `get_stock_by_location_and_product_for_update` | Same lookup with `SELECT … FOR UPDATE` row-lock — used when reserving, so concurrent reservations can't oversell |
| `get_stock_by_id_for_update` | Row-locked by-id lookup — used when releasing/fulfilling a reservation |
| `get_reservation_by_id` | Loads a `StockReservation` by id (for release/fulfill) |
| `initialize_stock` | Creates the row for a brand-new (location, product) pair |
| `update_quantity_stock(stock)` | Just commits — caller mutates `stock.quantity` first |
| `create_movement(movement)` | Append-only insert |
| `list_stock_movements` | Filters by `stock_id`, orders `created_at DESC`, defaults to `limit=100` |
| `get_stock_levels` | Optional filters: `location_id`, `product_id`. Returns current `quantity` and `reorder_point` per row. Uses `selectinload(product, location)` to avoid N+1 |

The reservation read paths take `FOR UPDATE` row locks so two orders confirming against the same stock row serialize rather than race past the available-quantity check.

### ReservationRepository — [reservation_repo.py](../app/inventory/repositories/reservation_repo.py)
`create_reservation(order_item_id, stock_id, quantity)` — builds a `RESERVED` `StockReservation` via the model factory and persists it. Status transitions on release/fulfill are done by the service mutating the loaded row.

---

## Service

[app/inventory/service.py](../app/inventory/service.py)

`InventoryService` takes all five repositories (product, category, location, stock, reservation) in its constructor. Methods are grouped into four sub-domains. It also exposes **`get_product(product_id)`** — a small read used cross-module by the orders service to validate a product before adding it to an order (raises `ProductNotFound`).

### Product
- **`create_product`**: trims `name`, uppercases `sku`, rejects empty values, and checks SKU uniqueness via `get_by_sku` before insert.
- **`update_product`**: requires at least one field; re-validates SKU uniqueness, but allows the SKU to match if it belongs to the same product (`existing.id != product_id`).
- **`activate_product` / `deactivate_product`**: thin wrappers over the repository — `DELETE /products/{id}` calls `deactivate_product` (soft delete).

### Category
- **`create_category`**: trims input, rejects empty name/description, checks name uniqueness via `get_by_name`.
- **`add_product_to_category` / `remove_product_from_category`**: both verify category and product exist before mutating the M:N collection. Adding is idempotent (no-op if already linked); the category-side `save_category` performs the commit.

### Stock
The interesting layer — every mutation produces a paired `StockMovement`.

- **`initialize_stock`**: coerces IDs and quantities via `abs(int(...))`, clamps `reorder_point` to `quantity`, verifies the location and product exist, and rejects `quantity <= 0`. Only call this for a (location, product) pair that has no row yet.
- **`add_stock`** (`IN`): increments `stock.quantity`, then writes a `StockMovement` with `previous_quantity` / `new_quantity` and the caller's `user_id`.
- **`remove_stock`** (`OUT`): same as `add_stock` but decrements, rejecting any request that would drive `quantity` negative.
- **`adjust_stock`** (`ADJUST`): **sets** `stock.quantity` to an absolute value (not a delta). Stores `abs(new - previous)` in `movement.quantity` so the audit row still carries a meaningful magnitude. Rejects negative targets.
- **`list_stock_movements`**: verifies the stock exists, then delegates to the repository (most recent first).
- **`get_stock_levels`**: pass-through to the repository — supports filtering by location, product, and low-stock.

**Audit invariant:** for every successful `add_stock` / `remove_stock` / `adjust_stock`, the service writes one `InventoryStock` update **and** one `StockMovement` row, in that order. Both go through the same `AsyncSession`.

### Reservations (driven by the orders module)
These back the order state machine; the orders service calls them inside its own transaction (so the order row and the reservation mutations commit together). They touch `reserved_quantity`, never `quantity` — except `fulfill`, which finally draws stock down.

- **`reserve_for_item(order_item_id, product_id, location_id, quantity)`**: rejects `quantity <= 0` (`InvalidQuantityStock`); loads the stock row **`FOR UPDATE`** (`StockNotFound` if missing); checks `quantity - reserved_quantity >= requested`, else `InsufficientStock` (409). On success, bumps `reserved_quantity` and creates a `RESERVED` reservation. *Called per line item by `confirm_order`.*
- **`release_for_item(reservation_id)`**: requires the reservation in `RESERVED` (`ReservationNotFound` / `InvalidReservationStatus`); decrements `reserved_quantity` and flips status to `RELEASED` — `quantity` is untouched (the goods were never shipped). *Called by `cancel_order`.*
- **`fulfill_for_item(reservation_id)`**: same guards, then decrements **both** `quantity` and `reserved_quantity` and sets status `FULFILLED` — the reservation becomes a real outflow. *Called by `complete_order`.*

**Concurrency:** all three take a `FOR UPDATE` lock on the stock row before mutating it, so overlapping confirmations against the same (product, location) can't both pass the availability check.

---

## Dependencies

[app/inventory/dependencies.py](../app/inventory/dependencies.py)

- **`provide_inventory_service`**: injects an `AsyncSession` and wires all five repositories (stock, product, category, location, reservation) into an `InventoryService`. Used by every inventory route, and re-exported to the orders module so both share one service.
- **`get_current_location`**: resolves the `X-Location-Id` header to a `Location` (400 if the header is missing, 404 if unknown). Backs the location-scoped stock routes and the orders `PATCH /orders/{id}/confirm` flow.

---

## Routers

[app/inventory/router.py](../app/inventory/router.py)

All endpoints under `/inventory` prefix. Every route requires a permission via `require_permission`; stock-mutating routes additionally require `get_current_user` so `current_user.id` is recorded on the `StockMovement`.

### Products
| Endpoint | Permission |
|---|---|
| `GET /inventory/products` | `product:view` |
| `GET /inventory/products/{id}` | `product:view` |
| `POST /inventory/products` | `product:create` |
| `PATCH /inventory/products/{id}` | `product:update` |
| `DELETE /inventory/products/{id}` | `product:deactivate` (soft delete) |
| `POST /inventory/products/{id}/activate` | `product:activate` |

### Categories
| Endpoint | Permission |
|---|---|
| `POST /inventory/categories` | `category:create` |
| `DELETE /inventory/categories/{id}` | `category:delete` |
| `POST /inventory/categories/{category_id}/products` | `category:create` |
| `DELETE /inventory/categories/{category_id}/products` | `category:remove` |

### Stock
| Endpoint | Permission |
|---|---|
| `POST /inventory/new` | `stock:create` (initialize a new stock row) |
| `POST /inventory/in` | `stock:in` |
| `POST /inventory/out` | `stock:out` |
| `POST /inventory/adjust` | `stock:adjust` |
| `GET /inventory/movements?stock_id&limit` | `stock:view` |
| `GET /inventory/stock?location_id&product_id` | `stock:view` |

### Locations
| Endpoint | Permission |
|---|---|
| `GET /inventory/locations` | `location:list` |
| `GET /inventory/locations/{id}` | `location:view` |
| `POST /inventory/locations` | `location:create` |
| `PATCH /inventory/locations/{id}` | `location:update` |
| `DELETE /inventory/locations/{id}` | `location:delete` (409 if the location still has stock) |

`location:list` and `location:view` are granted to both admin and employee; create/update/delete are admin-only.

---

## Errors

[app/inventory/exceptions.py](../app/inventory/exceptions.py)

Typed domain exceptions extending the shared `AppError` base (via the module's `InventoryError` — 400 / `INVENTORY_ERROR`). The service raises these directly — there are no raw `ValueError`s left — so each maps to a proper status code through the global `AppError` handler.

| Exception | HTTP | Code |
|---|---|---|
| `ProductNotFound` | 404 | `PRODUCT_NOT_FOUND` |
| `ProductAlreadyExits` | 409 | `PRODUCT_ALREADY_EXISTS` |
| `ProductNameIsRequired` / `SKUIsRequired` | 400 | `PRODUCT_NAME_IS_REQUIRED` / `SKU_IS_REQUIRED` |
| `CategoryNotFound` | 404 | `CATEGORY_NOT_FOUND` |
| `CategoryAlreadyExists` | 409 | `CATEGORY_ALREADY_EXISTS` |
| `CategoryNameIsRequired` / `CategoryDescriptionIsRequired` | 400 | `CATEGORY_NAME_IS_REQUIRED` / `CATEGORY_DESCRIPTION_IS_REQUIRED` |
| `LocationNotFound` | 404 | `LOCATION_NOT_FOUND` |
| `LocationAlreadyExists` | 409 | `LOCATION_ALREADY_EXISTS` |
| `LocationHasStock` | 409 | `LOCATION_HAS_STOCK` |
| `LocationNameIsRequired` / `LocationCityIsRequired` / `LocationAddressIsRequired` | 400 | `LOCATION_*_IS_REQUIRED` |
| `InvalidLocation` | 400 | `INVALID_LOCATION_ID` |
| `StockNotFound` | 404 | `STOCK_NOT_FOUND` |
| `StockAlreadyExists` | 409 | `STOCK_ALREADY_EXISTS` |
| `StockNegative` | 400 | `STOCK_NEGATIVE` |
| `InsufficientStock` | 409 | `INSUFFICIENT_STOCK` |
| `InvalidQuantityStock` | 400 | `INVALID_QUANTITY_STOCK` |
| `InvalidProductOrLocation` | 400 | `INVALID_PRODUCT_OR_LOCATION` |
| `NoParametersProvide` | 400 | `NO_PARAMETERS_PROVIDE` |
| `ReservationNotFound` | 404 | `RESERVATION_NOT_FOUND` |
| `InvalidReservationStatus` | 409 | `INVALID_RESERVATION_STATUS` |

---

## Flow Diagram — Stock Mutation (`in` / `out` / `adjust`)

```
POST /inventory/{in|out|adjust}
      │  (payload: product_id, location_id, quantity)
      ▼
┌──────────────────────────────┐
│ require_permission(stock:*)  │
│ get_current_user → user_id   │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ get_stock_by_location_       │ ← StockNotFound (404) if not initialized
│ and_product(product, loc)    │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ validate quantity            │   in:     stock.qty += q
│  (out: qty >= delta)         │   out:    stock.qty -= q  (>= 0)
│  (adjust: target >= 0)       │   adjust: stock.qty  = q
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ update_quantity_stock(stock) │   ← commit #1: new on-hand
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ create_movement(             │   ← commit #2: audit row
│   movement_type, quantity,   │     (previous_qty, new_qty,
│   previous_qty, new_qty,     │      created_by=user_id)
│   created_by)                │
└──────────────┬───────────────┘
               ▼
       StockMovementResponse
```

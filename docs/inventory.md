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
└────────┬─────────┘          └──────────────────┘
         │ N:1
         ▼
   ┌────────────┐
   │  Location  │
   └────────────┘
```

**Core principle:** `InventoryStock` is the only mutable quantity. Every change to `stock.quantity` is paired with an immutable `StockMovement` capturing `previous_quantity`, `new_quantity`, `movement_type`, and `created_by`.

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
Minimal model: `id`, `name`, `address`, plus a backref to its stocks. There is no create/update/delete API for locations in this module — only `get_location` is exposed by the repository.

### InventoryStock — [stock.py](../app/inventory/models/stock.py)
| Field | Notes |
|---|---|
| `location_id`, `product_id` | FKs; the pair is treated as a logical unique key (looked up via `get_stock_by_location_and_product`) |
| `quantity` | Current on-hand quantity |
| `reserved_quantity` | Reserved by orders module — not modified here |
| `reorder_point` | Threshold for `low_stock` queries (`quantity < reorder_point`) |

### StockMovement — [stock.py](../app/inventory/models/stock.py)
Append-only audit row. Carries `movement_type` (`IN` / `OUT` / `ADJUST`), the delta `quantity`, both `previous_quantity` and `new_quantity`, and `created_by` (FK → `users.id`). For `ADJUST`, `quantity` stores the absolute difference between the new and old value.

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
`get_location` only — location CRUD lives outside this module.

### StockRepository
| Method | Notes |
|---|---|
| `get_stock` | Lookup by stock id |
| `get_stock_by_location_and_product` | Lookup by the logical (location, product) key — the entry point for every `in/out/adjust` |
| `initialize_stock` | Creates the row for a brand-new (location, product) pair |
| `update_quantity_stock(stock)` | Just commits — caller mutates `stock.quantity` first |
| `create_movement(movement)` | Append-only insert |
| `list_stock_movements` | Filters by `stock_id`, orders `created_at DESC`, defaults to `limit=100` |
| `get_stock_levels` | Optional filters: `location_id`, `product_id`, `low_stock` (`quantity < reorder_point`). Uses `selectinload(product, location)` to avoid N+1 |

A docstring at the bottom of [stock_repo.py](../app/inventory/repositories/stock_repo.py) reserves slots for `get_available_stock`, `reserve_stock`, `release_reservation`, `fulfill_reservation` — these will be driven by the orders module.

---

## Service

[app/inventory/service.py](../app/inventory/service.py)

`InventoryService` takes all four repositories in its constructor. Methods are grouped into three sub-domains.

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

---

## Dependencies

[app/inventory/dependencies.py](../app/inventory/dependencies.py)

Single dependency — `provide_inventory_service` — that injects an `AsyncSession` and wires all four repositories into an `InventoryService` instance. Used by every inventory route.

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
| `GET /inventory/stock?location_id&product_id&low_stock` | `stock:view` |

---

## Errors

The inventory service currently raises plain `ValueError`s (e.g. `"product with SKU 'X' already exists"`, `"stock cannot be negative"`, `"invalid location id"`). Only `list_movements` translates them — it catches `ValueError` and re-raises as `HTTPException(404)`. The rest will surface as 500s until typed domain exceptions are added.

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
│ get_stock_by_location_       │ ← ValueError if pair not initialized
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

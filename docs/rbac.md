# RBAC Module

Role-Based Access Control system. Users get permissions through roles, not directly. Permissions are checked via FastAPI dependencies before protected endpoints execute.

---

## Architecture Overview
```
┌─────────┐         ┌─────────┐         ┌─────────────┐
│  Users  │────────▶│  Roles  │────────▶│ Permissions │
└─────────┘  M:N    └─────────┘  M:N    └─────────────┘

User → has roles → roles have permissions → permission check passes/fails
```

**Core principle:** Indirect access control. Users don't own permissions; they own roles. Roles bundle permissions. Permission checks traverse `user.roles → role.permissions`.

---

## Models

[app/rbac/models/](../app/rbac/models/)

### Role
| Field | Notes |
|---|---|
| `name` | Unique, indexed — the seeded roles are `admin`, `employee`, `client` |
| `description` | Human-readable role purpose |
| `permissions` | Many-to-many via `role_permissions` association table |
| `users` | Backref from `user_roles` — all users assigned this role |

### Permission
| Field | Notes |
|---|---|
| `code` | Unique permission identifier (e.g., `users:view`, `stock:in`) |
| `description` | What the permission grants |
| `roles` | Backref from `role_permissions` |

### Association Tables
- **`user_roles`**: Links `User.id` ↔ `Role.id`
- **`role_permissions`**: Links `Role.id` ↔ `Permission.id`

Both use composite primary keys `(left_id, right_id)` with foreign key constraints and cascading deletes.

---

## Bootstrap / Seeding

[app/bootstraps/](../app/bootstraps/)

`seed_all()` orchestrates both steps and is **run once at application startup** to populate permissions then roles.

### seed_permissions()
Creates all permission records from the constants under [app/core/constants/](../app/core/constants/) — `SYSTEM_PERMISSIONS`, `INVENTORY_PERMISSIONS`, `USER_PERMISSIONS`, `ORDER_PERMISSIONS`. The codes follow a `resource:action` convention, e.g.:
```python
SYSTEM_PERMISSIONS = [
    "roles:view", "roles:create", "roles:update",
    "role:assign_permission", "role:remove_permission",
    "users:assign_role", "users:remove_role",
]
```

### seed_roles()
Creates role records and assigns permissions based on the `SYSTEM_ROLES` constant:

```python
SYSTEM_ROLES = {
    "admin": SYSTEM_PERMISSIONS + INVENTORY_PERMISSIONS
             + USER_PERMISSIONS + ORDER_PERMISSIONS,   # everything
    "employee": ["product:view", "product:create", ..., "order:complete"],
    "client": [],   # no permissions — relies on self-scoped/public routes
}
```

**Key insight:** Permission matrices are defined in code as constants, not in the database. Roles are seeded with their permissions at startup. Changes to the permission model require a re-seed (or migration). Note `client` is intentionally permission-less — client-facing access comes from self-scoped routes (`GET /orders/me`) and public ones (`GET /orders/code/{code}`), not RBAC grants.

---

## Schemas

[app/rbac/schemas.py](../app/rbac/schemas.py)

Single-file Pydantic models — no separate DTO layer. Role/permission *assignment* carries no request body; the IDs travel as path params (`/users/{user_id}/roles/{role_id}`), so only the create/update/permission-payload requests exist.

| Request | Fields |
|---|---|
| `RoleCreateRequest` | `name` (2–100), `description` (≤255, optional) |
| `RoleUpdateRequest` | `name`, `description` — both optional |
| `AddPermissionToRoleRequest` / `RemovePermissionFromRoleRequest` | `permission_id` (UUID) |

| Response | Fields |
|---|---|
| `RoleResponse` | `id`, `name`, `description`, nested `permissions: List[PermissionResponse]` |
| `PermissionResponse` | `id`, `name` |
| `UserRoleResponse` | `user_id`, `role_id` |

All response models use `from_attributes=True` to read straight off ORM objects.

---

## Repositories

[app/rbac/repositories/](../app/rbac/repositories/)

### RoleRepository
Pure data access for role operations.

| Method | Notes |
|---|---|
| `get_by_id` | Primary key lookup |
| `get_by_name` | Used for uniqueness checks during role creation |
| `get_all` | Returns all roles (typically small dataset) |
| `create` | Adds role and commits |
| `user_has_role` | Checks existence in `user_roles` table |
| `add_role_to_user` | Inserts into `user_roles` |
| `remove_role_from_user` | Deletes from `user_roles` |
| `role_has_permission` | Checks existence in `role_permissions` table |
| `add_permission_to_role` | Inserts into `role_permissions` |
| `remove_permission_from_role` | Deletes from `role_permissions` |
| `get_user_with_roles_and_permissions` | **Critical query** — eagerly loads `user.roles.permissions` in one query for permission checking |

### PermissionRepository
| Method | Notes |
|---|---|
| `get_by_id` | Primary key lookup |
| `get_by_code` | Finds permission by code string |
| `create` | Adds permission and commits |

---

## Service

[app/rbac/service.py](../app/rbac/service.py)

Business logic for role and permission management. All operations go through the service.

### Role Management
- **`create_role`**: Checks name uniqueness before insert → raises `RoleAlreadyExists (409)` on conflict
- **`update_role`**: Validates name uniqueness when changing names, skipping the role being updated
- **`list_roles`**: Returns all roles (no pagination — roles are typically a small set)

### Role-User Assignment
- **`assign_role_to_user`**: Checks if role exists, checks if user already has it → raises `RoleAlreadyAssignedToUser` to prevent duplicate assignments
- **`remove_role_from_user`**: Checks if the assignment exists before removal → raises `UserRoleNotFound` if not

### Role-Permission Assignment
- **`add_permission_to_role`**: Validates both role and permission exist, checks for duplicate assignment → raises `PermissionAlreadyAssigned`
- **`remove_permission_from_role`**: Checks existence before removal → raises `RolePermissionNotFound`

### Permission Checking ⭐
**`ensure_permission(user_id, permission_code)`** — the core authorization check:
1. Loads user with all roles and permissions in **one query** via `get_user_with_roles_and_permissions`
2. Loops through `user.roles → role.permissions`
3. Checks if any permission has `code == permission_code`
4. If not found → raises `PermissionDenied (403)`

This is called by the `require_permission` decorator on every protected endpoint.

---

## Dependencies

[app/rbac/dependencies.py](../app/rbac/dependencies.py)

### get_rbac_service
FastAPI dependency that injects an `AsyncSession` and returns an `RBACService` instance. Used in routers to get the service.

### require_permission(permission_code: str)
**The authorization decorator.** Returns a FastAPI dependency that:
1. Injects `current_user` (from JWT)
2. Injects `rbac_service`
3. Calls `rbac_service.ensure_permission(current_user.id, permission_code)`
4. If `PermissionDenied` is raised → converts to `HTTPException(403)`

**Usage in routers:**
```python
@router.post(
    "/roles",
    dependencies=[Depends(require_permission("role:create"))]
)
async def create_role(...):
    ...
```

The permission check happens **before** the endpoint function executes. If it fails, the route handler never runs.

**On the token `roles` claim:** access tokens embed the user's role names (see the `auth` module), but `require_permission` does **not** trust that claim — `ensure_permission` re-loads `user.roles → permissions` from the DB on every call. So a revoked role or permission takes effect immediately, not only after the next token refresh. The claim is currently informational (e.g. for the client), not an authorization shortcut.

---

## Routers

[app/rbac/routers.py](../app/rbac/routers.py)

HTTP layer for role and permission management, under the `/rbac` prefix. Every route is permission-gated.

| Endpoint | Permission Required |
|---|---|
| `POST /rbac/roles` | `roles:create` |
| `PATCH /rbac/roles/{role_id}` | `roles:update` |
| `GET /rbac/roles` | `roles:view` |
| `POST /rbac/roles/{role_id}/permissions` | `role:assign_permission` |
| `DELETE /rbac/roles/{role_id}/permissions` | `role:remove_permission` |
| `POST /rbac/users/{user_id}/roles/{role_id}` | `users:assign_role` |
| `DELETE /rbac/users/{user_id}/roles/{role_id}` | `users:remove_role` |

---

## Errors

[app/rbac/exceptions.py](../app/rbac/exceptions.py)

Domain-specific exceptions extending `AppError` (via the module's `RbacError` base — 400 / `RBAC_ERROR`).

| Exception | HTTP | Code |
|---|---|---|
| `RoleNotFound` | 404 | `ROLE_NOT_FOUND` |
| `RoleAlreadyExists` | 409 | `ROLE_ALREADY_EXISTS` |
| `PermissionNotFound` | 404 | `PERMISSION_NOT_FOUND` |
| `PermissionAlreadyAssigned` | 409 | `PERMISSION_ALREADY_ASSIGNED` |
| `RoleAlreadyAssignedToUser` | 409 | `ROLE_ALREADY_ASSIGNED_TO_USER` |
| `UserRoleNotFound` | 404 | `USER_ROLE_NOT_FOUND` |
| `RolePermissionNotFound` | 404 | `ROLE_PERMISSION_NOT_FOUND` |
| `PermissionDenied` | 403 | `PERMISSION_DENIED` |

---

## Flow Diagram

```
┌─────────────────┐
│  API Request    │
└────────┬────────┘
│
▼
┌─────────────────────────┐
│  get_current_user       │  ← Extracts user from JWT
└────────┬────────────────┘
│
▼
┌─────────────────────────┐
│  require_permission()   │  ← FastAPI dependency
│  - permission_code      │
└────────┬────────────────┘
│
▼
┌──────────────────────────────────────┐
│  ensure_permission()                 │
│  1. Load user.roles.permissions      │
│  2. Check if permission exists       │
│  3. Raise PermissionDenied if not    │
└────────┬─────────────────────────────┘
│
┌────┴────┐
│         │
▼         ▼
┌───────┐  ┌──────────────┐
│ Allow │  │ 403 Forbidden│
└───────┘  └──────────────┘
```
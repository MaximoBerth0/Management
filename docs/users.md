# User Module

Handles user lifecycle: registration, profile management, and account status (enable/disable). Authentication (JWT) and role assignment live in separate modules (`auth`, `rbac`).

---

## Model

[app/users/model.py](../app/users/model.py)

| Field | Notes |
|---|---|
| `email`, `username` | Both unique + indexed — two lookup paths for auth |
| `hashed_password` | Raw password never stored |
| `is_active` | Soft disable flag; checked at auth time |
| `created_at`, `updated_at` | `updated_at` is nullable, set on change |
| `disabled_at`, `disabled_by`, `reason` | Audit trail written on disable, cleared on re-enable |
| `roles` | Many-to-many via `user_roles` association table, loaded with `selectin` to avoid N+1 |
| `refresh_tokens` | `cascade="all, delete-orphan"` — tokens are invalidated when the user is deleted |

---

## Schemas

[app/users/schemas.py](../app/users/schemas.py)

Single-file Pydantic models — no separate DTO/command layer. The router passes plain fields (e.g. `email=`, `username=`, `password=`) into the service, which owns password hashing. Responses derive from ORM objects via `ORMModel` (`from_attributes=True`) and never expose `hashed_password`.

| Request | Fields |
|---|---|
| `UserCreateRequest` | `email` (`EmailStr`), `username` (3–150), `password` (≥8) |
| `UserUpdateRequest` | `email`, `username` — both optional (partial profile update) |
| `DisableUserRequest` | `reason` (1–500) |
| `UserStatusUpdateRequest` | `is_active` (bool) |

| Response | Fields |
|---|---|
| `UserReadResponse` | `id`, `email`, `username`, `is_active`, `created_at` |
| `UserListItemResponse` | `id`, `email`, `username`, `is_active` |

---

## Repository

[app/users/repository.py](../app/users/repository.py)

Pure data access — no business logic. Each method is a single SQLAlchemy operation followed by `commit` + `refresh`. The `update_profile` method uses `setattr` over a dict to stay generic without coupling the repository to specific field names.

Methods:

| Method | Notes |
|---|---|
| `get_by_id` | Uses `session.get` (primary key lookup, hits identity map first) |
| `get_by_email` | Full `select` query — used by auth and uniqueness checks |
| `list_users` | Paginated with `skip`/`limit` |
| `create_user` | Adds and commits; caller builds the ORM object |
| `update_profile` | Generic field update via `setattr` |
| `enable_account` / `disable_account` | Only flips `is_active`; audit fields are set by the service before calling |

---

## Service

[app/users/service.py](../app/users/service.py)

Business logic layer. All operations go through the service — routers never call the repository directly.

Key decisions:

- **`register_user`**: Email uniqueness is checked at the service level before insert, raising `UserAlreadyExists (409)` instead of relying on a DB unique-constraint error. This gives a clean, typed error before hitting the database constraint.
- **`update_profile`**: Uses `model_dump(exclude_unset=True)` so only fields the client explicitly sent are updated (partial update semantics). A secondary `forbidden_fields` filter strips any fields that must not change via this endpoint (`id`, `is_active`, timestamps) — defense in depth against accidental exposure.
- **`list_users`**: Caps `limit` at 100 server-side regardless of what the caller sends.
- **`disable_account`**: Sets `disabled_at`, `disabled_by`, and `reason` on the ORM object before delegating the `is_active = False` flip to the repository. The audit fields and the status flag are committed atomically in one transaction.
- **`enable_account`**: Clears all three audit fields (`disabled_at`, `disabled_by`, `reason`) to signal a clean slate — not just flipping `is_active`.

---

## Dependencies

[app/users/dependencies.py](../app/users/dependencies.py)

Single dependency — `provide_user_service` — that injects an `AsyncSession` and returns a `UserService`. Keeps FastAPI's DI wiring decoupled from the service constructor.

---

## Routers

[app/users/router.py](../app/users/router.py)

Thin HTTP layer under the `/users` prefix. Calls the service and returns the result; for `PUT /users/me` it forwards `data.model_dump(exclude_unset=True)` so only sent fields update.

| Endpoint | Auth | Permission |
|---|---|---|
| `POST /users/register` | None | — |
| `PUT /users/me` | JWT required | — (self-scoped) |
| `GET /users/list` | JWT required | `users:view` |
| `GET /users/{user_id}` | JWT required | `users:view` |
| `GET /users/email/{email}` | JWT required | `users:view` |
| `PATCH /users/{user_id}/disable-account` | JWT required | `users:disable` |
| `PATCH /users/{user_id}/enable` | JWT required | `users:enable` |

Registration is intentionally public. `PUT /users/me` only requires authentication (self-scoped). The admin operations (list, lookups, disable, enable) require RBAC permissions checked via `require_permission` — note disable and enable are gated by **separate** permissions (`users:disable` / `users:enable`).

---

## Errors

[app/users/exceptions.py](../app/users/exceptions.py)

Domain-specific exceptions that extend a shared `AppError` base (via the module's `UserError` — 400 / `USER_ERROR`). Each carries a typed `error_code` string for machine-readable error handling on the client side.

| Exception | HTTP | Code |
|---|---|---|
| `UserNotFound` | 404 | `USER_NOT_FOUND` |
| `UserAlreadyExists` | 409 | `USER_ALREADY_EXISTS` |
| `UserInactive` | 403 | `USER_INACTIVE` |

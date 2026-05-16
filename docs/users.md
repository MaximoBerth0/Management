# User Module

Handles user lifecycle: registration, profile management, and account status (enable/disable). Authentication (JWT) and role assignment live in separate modules (`auth`, `rbac`).

---

## Model

[app/users/models.py](../app/users/models.py)

| Field | Notes |
|---|---|
| `email`, `username` | Both unique + indexed — two lookup paths for auth |
| `hashed_password` | Raw password never stored |
| `is_active` | Soft disable flag; checked at auth time |
| `disabled_at`, `disabled_by`, `reason` | Audit trail written on disable, cleared on re-enable |
| `roles` | Many-to-many via `user_roles` association table, loaded with `selectin` to avoid N+1 |
| `refresh_tokens` | `cascade="all, delete-orphan"` — tokens are invalidated when the user is deleted |

---

## Schemas

[app/users/schemas/](../app/users/schemas/)

Two schema layers are intentional:

**`api.py` — HTTP boundary:** Pydantic models that validate incoming requests and shape outgoing responses. Passwords come in as plain strings; responses never expose `hashed_password`.

**`command.py` — service boundary:** Internal transfer objects passed from router → service. The router translates `UserCreateRequest.password` into `CreateUserCommand.hashed_password` before handing off — keeping the hashing responsibility inside the service, not on the caller.

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

Single dependency — `get_user_service` — that injects an `AsyncSession` and returns a `UserService`. Keeps FastAPI's DI wiring decoupled from the service constructor.

---

## Routers

[app/users/routers.py](../app/users/routers.py)

Thin HTTP layer. Translates API schemas → command schemas, calls the service, returns the result.

| Endpoint | Auth | Permission |
|---|---|---|
| `POST /users/register` | None | — |
| `PUT /users/me` | JWT required | — |
| `GET /users/list` | JWT required | `users:view` |
| `GET /users/{user_id}` | JWT required | `users:view` |
| `GET /users/email/{email}` | JWT required | `users:view` |
| `PATCH /users/{user_id}/disable-account` | JWT required | `users:update` |
| `PATCH /users/{user_id}/enable` | JWT required | `users:update` |

Registration is intentionally public. All admin operations (list, disable, enable) require RBAC permissions checked via `require_permission`.

---

## Errors

[app/users/errors.py](../app/users/errors.py)

Domain-specific exceptions that extend a shared `AppError` base. Each carries a typed `error_code` string for machine-readable error handling on the client side.

| Exception | HTTP | Code |
|---|---|---|
| `UserNotFound` | 404 | `USER_NOT_FOUND` |
| `UserAlreadyExists` | 409 | `USER_ALREADY_EXISTS` |
| `UserInactive` | 403 | `USER_INACTIVE` |

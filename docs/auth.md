# Auth Module

JWT-based authentication system. Users authenticate with email/password and receive short-lived access tokens plus long-lived refresh tokens. Password reset is handled via email with a time-limited single-use token.

---

## Architecture Overview
```
┌─────────┐         ┌───────────────┐         ┌──────────────────────┐
│  Client │────────▶│  Access Token │────────▶│  get_current_user()  │
└─────────┘  JWT    └───────────────┘  verify  └──────────────────────┘

┌─────────┐         ┌───────────────┐         ┌──────────────────────┐
│  Client │────────▶│ Refresh Token │────────▶│  refresh_session()   │
└─────────┘  opaque └───────────────┘  rotate  └──────────────────────┘
```

**Core principle:** Access tokens are short-lived JWTs verified statelessly. Each access token also embeds the user's **role names** as a `roles` claim, so downstream RBAC checks can read them straight off the token without a DB round-trip (see the `rbac` module). Refresh tokens are opaque random strings stored (hashed) in the DB — revocation is possible at any time. Password reset tokens are single-use and expire in 10 minutes.

---

## Models

[app/auth/model.py](../app/auth/model.py)

### RefreshToken
| Field | Notes |
|---|---|
| `token_hash` | Unique, indexed — SHA-256 hex digest of the raw token; raw token is only ever in memory/transit |
| `user_id` | FK → `users.id`, cascades on delete |
| `expires_at` | Timezone-aware expiry timestamp |
| `is_revoked` | Soft-revocation flag; queries filter on `is_revoked = false` |
| `created_at` | Server-side default via `func.now()` |

### PasswordResetToken
| Field | Notes |
|---|---|
| `token` | Unique, indexed — URL-safe random string |
| `user_id` | FK → `users.id`, cascades on delete |
| `expires_at` | 10-minute window from creation |
| `used` | Marks token as consumed; `get_valid` filters on `used = false` |
| `created_at` | Server-side default |

---

## Security Utilities

[app/core/security/](../app/core/security/)

### tokens.py
| Function | Notes |
|---|---|
| `create_token(*, subject, token_type, expires_delta, extra_claims)` | Generic signer — builds the base payload and merges any `extra_claims` |
| `create_access_token(user_id, roles=None)` | Wraps `create_token` for `type="access"`; passes `roles` (defaulting to `[]`) as an extra claim |
| `decode_token(token)` | Decodes/verifies the signature; maps `ExpiredSignatureError → TokenExpired`, any other `PyJWTError → TokenInvalid` |
| `verify_access_token(token)` | `decode_token` + asserts `type == "access"` — raises `TokenInvalid` on mismatch; returns the full payload |
| `generate_refresh_token()` | `secrets.token_urlsafe(32)` — raw token returned to client; SHA-256 hash stored in DB |
| `generate_reset_token()` | Same generation strategy as `generate_refresh_token()` — separate function for clarity |

**JWT payload fields:** `sub` (user_id as str), `type` (token type), `iat`, `exp`, `jti` (UUID per token), and on access tokens `roles` (list of role-name strings).

### passwords.py
Uses `argon2-cffi`'s `PasswordHasher` directly (a module-level `ph` instance). Exposes `hash_password` and `verify_password`; the latter catches `VerificationError` / `InvalidHashError` and returns `False` rather than raising.

---

## Schemas

[app/auth/schemas.py](../app/auth/schemas.py)

Single-file Pydantic models — request bodies plus the one response shape. The router passes plain fields (e.g. `data.email`, `data.refresh_token`) into the service, which returns a `TokenResponse` directly; there is no separate DTO layer.

| Request | Fields |
|---|---|
| `LoginRequest` | `email` (`EmailStr`), `password` (`Field(min_length=8, max_length=50)`) |
| `LogoutRequest` / `RefreshTokensRequest` | `refresh_token` |
| `ForgotPasswordRequest` | `email` (`EmailStr`) |
| `ResetPasswordRequest` | `token`, `new_password` |
| `ChangePasswordRequest` | `old_password`, `new_password` |

`TokenResponse` — output with `access_token`, `refresh_token`, `token_type: Literal["bearer"] = "bearer"`.

All password inputs carry an 8–50 length bound at the schema boundary: `LoginRequest.password`, plus `new_password` on both `ResetPasswordRequest` and `ChangePasswordRequest`. (`old_password` is unbounded — it only has to match the stored hash.)

---

## Repositories

[app/auth/repositories/](../app/auth/repositories/)

### RefreshTokenRepository
| Method | Notes |
|---|---|
| `create` | Adds token record and commits |
| `get_by_token` | Lookup by token string (no revocation check) |
| `get_active` | Lookup filtering `is_revoked = false` — used before consuming a token |
| `revoke` | Sets `is_revoked = true` by token ID |
| `revoke_all_for_user` | Bulk-revokes all active tokens for a user — called on password reset |

### PasswordResetTokenRepository
| Method | Notes |
|---|---|
| `create` | Adds reset token record and commits |
| `get_valid` | Lookup filtering `used = false` |
| `invalidate` | Marks a single token as used |
| `invalidate_all_for_user` | Invalidates all active reset tokens before issuing a new one — prevents token accumulation |

---

## Service

[app/auth/service.py](../app/auth/service.py)

All auth flows go through `AuthService`. Constructor-injected dependencies: `UserRepository`, `RefreshTokenRepository`, `PasswordResetTokenRepository`, `Mailer`.

### login
1. Looks up user by email
2. Verifies password with `verify_password` — raises `InvalidCredentials (401)` on any failure (intentionally conflates "user not found" and "wrong password")
3. Creates the access token, embedding `[role.name for role in user.roles]` as the `roles` claim
4. Generates + persists a refresh token with expiry
5. Returns `TokenResponse`

### logout
1. Looks up active refresh token → raises `TokenInvalid` if not found or already revoked
2. Revokes it by ID

### refresh_session
1. Looks up active refresh token → raises `TokenExpired` if not found
2. Checks `expires_at` against now → raises `TokenExpired` if stale
3. **Rotates:** revokes old token, creates new refresh token
4. Re-fetches the user and issues a new access token, re-embedding the current `roles` (so role changes take effect on refresh)
5. Returns `TokenResponse`

### forgot_password
1. Looks up user by email — **silently returns if user doesn't exist** (prevents email enumeration)
2. Invalidates all existing reset tokens for the user
3. Generates a new token, stores it with a 10-minute expiry
4. Sends email via `Mailer.send_reset_email`

### reset_password
1. Looks up valid (unused) token → raises `TokenInvalid` if not found
2. Checks `expires_at` → raises `TokenExpired` if stale
3. Hashes new password and saves to user
4. Marks reset token as used
5. **Revokes all active refresh tokens** — forces re-login on all devices

### change_password
1. Verifies current password → raises `InvalidCredentials` if wrong
2. Hashes and saves new password
3. **Revokes all active refresh tokens** — same security guarantee as reset

---

## Dependencies

[app/auth/dependencies.py](../app/auth/dependencies.py)

### get_current_user
FastAPI dependency that powers all authenticated routes.
1. Extracts Bearer token via `OAuth2PasswordBearer`
2. Calls `verify_access_token` — raises `HTTPException(401)` on `TokenInvalid` or `TokenExpired`
3. Reads `sub` claim as `user_id`
4. Fetches user from DB → raises `HTTPException(401)` if not found
5. Returns the `User` ORM object

**Usage in routers:**
```python
@router.post("/change-password")
async def change_password(
    current_user: User = Depends(get_current_user),
    ...
):
```

### get_auth_service
Dependency that wires all repositories and the mailer into `AuthService`. Used in every auth router.

---

## Routers

[app/auth/routers.py](../app/auth/routers.py)

All endpoints under `/auth` prefix.

| Endpoint | Auth Required | Notes |
|---|---|---|
| `POST /auth/login` | No | Returns access + refresh tokens |
| `POST /auth/refresh` | No | Rotates refresh token, issues new access token |
| `POST /auth/logout` | No | Revokes refresh token (204) |
| `POST /auth/forgot` | No | Sends reset email, silent on unknown email (204) |
| `POST /auth/reset` | No | Consumes reset token, sets new password (204) |
| `POST /auth/change-password` | Yes (`get_current_user`) | Requires old password (204) |

---

## Errors

[app/auth/exceptions.py](../app/auth/exceptions.py)

All extend `AuthError` (base HTTP 401).

| Exception | HTTP | Code |
|---|---|---|
| `InvalidCredentials` | 401 | `INVALID_CREDENTIALS` |
| `TokenExpired` | 401 | `TOKEN_EXPIRED` |
| `TokenInvalid` | 401 | `TOKEN_INVALID` |

---

## Flow Diagrams

### Login
```
POST /auth/login
      │
      ▼
┌─────────────────────┐
│  verify credentials │ ← InvalidCredentials(401) if fail
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  create access JWT  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  persist refresh    │
│  token + expiry     │
└────────┬────────────┘
         │
         ▼
   TokenResponse
```

### Refresh
```
POST /auth/refresh
      │
      ▼
┌──────────────────────┐
│  get_active(token)   │ ← TokenExpired(401) if not found
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  check expires_at    │ ← TokenExpired(401) if stale
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  revoke old token    │
│  create new token    │ ← rotation — old token can't be reused
└────────┬─────────────┘
         │
         ▼
   TokenResponse
```

### Password Reset
```
POST /auth/forgot              POST /auth/reset
      │                               │
      ▼                               ▼
┌─────────────┐              ┌─────────────────────┐
│ find user   │              │ get_valid(token)     │ ← TokenInvalid if not found
│ (silent 204 │              └────────┬────────────┘
│  if missing)│                       │
└──────┬──────┘                       ▼
       │                     ┌─────────────────────┐
       ▼                     │ check expires_at     │ ← TokenExpired if stale
┌──────────────────┐         └────────┬────────────┘
│ invalidate old   │                  │
│ reset tokens     │                  ▼
└──────┬───────────┘         ┌─────────────────────┐
       │                     │ hash + save password │
       ▼                     │ invalidate token     │
┌──────────────────┐         │ revoke all refresh   │
│ create token     │         │ tokens               │
│ (10 min expiry)  │         └─────────────────────┘
└──────┬───────────┘
       │
       ▼
  send email
```

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

**Core principle:** Access tokens are short-lived JWTs verified statelessy. Refresh tokens are opaque random strings stored (hashed) in the DB — revocation is possible at any time. Password reset tokens are single-use and expire in 10 minutes.

---

## Models

[app/auth/models.py](../app/auth/models.py)

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
| `create_access_token(user_id)` | Signs a JWT with `sub`, `type="access"`, `iat`, `exp`, `jti` claims |
| `verify_access_token(token)` | Decodes and asserts `type == "access"` — raises `TokenInvalid` on mismatch |
| `generate_refresh_token()` | `secrets.token_urlsafe(32)` — raw token returned to client; SHA-256 hash stored in DB |
| `generate_reset_token()` | Same generation strategy as `generate_refresh_token()` — separate function for clarity |

**JWT payload fields:** `sub` (user_id as str), `type` (token type), `iat`, `exp`, `jti` (UUID per token).

### passwords.py
Uses `passlib.CryptContext` with the scheme from `settings.PASSWORD_HASH_SCHEME` (bcrypt by default). Exposes `hash_password` and `verify_password`.

---

## Schemas

[app/auth/schemas/](../app/auth/schemas/)

**`dto.py` — Internal transfer objects:**
- `LoginDTO`, `LogoutDTO`, `RefreshSessionDTO`
- `ForgotPasswordDTO`, `ResetPasswordDTO`, `ChangePasswordDTO`
- `TokenResponseDTO` — output with `access_token`, `refresh_token`, `token_type="bearer"`

**`api.py` — HTTP boundary:**
Pydantic request/response models. The router translates API schemas → DTOs before calling the service. Passwords validated at 8–50 characters on input.

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
3. Creates access token + refresh token, persists refresh token with expiry
4. Returns `TokenResponseDTO`

### logout
1. Looks up active refresh token → raises `TokenInvalid` if not found or already revoked
2. Revokes it by ID

### refresh_session
1. Looks up active refresh token → raises `TokenExpired` if not found
2. Checks `expires_at` against now → raises `TokenExpired` if stale
3. **Rotates:** revokes old token, creates new refresh token
4. Issues new access token
5. Returns `TokenResponseDTO`

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

[app/auth/errors.py](../app/auth/errors.py)

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

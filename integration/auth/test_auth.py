"""
the auth module test evaluates the following:

- Happy path      - normal expected behavior
- Validation      - bad input, missing fields
- Auth/Permission - unauthorized, forbidden
- Edge cases      - duplicates, not found, etc.

Fixtures and helpers come from integration/conftest.py:
- `admin_user`  : user with the admin role (all permissions)
- `plain_user`  : authenticated user with no role / no permissions
- `auth_headers`: builds the Authorization header for a user
"""

from datetime import datetime, timedelta, timezone

from app.auth.model import PasswordResetToken

# POST /auth/login

async def test_login_success(client, plain_user):
    response = await client.post(
        "/auth/login",
        json={"email": plain_user.email, "password": "password123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


async def test_login_wrong_password(client, plain_user):
    response = await client.post(
        "/auth/login",
        json={"email": plain_user.email, "password": "wrongpassword"},
    )
    assert response.status_code == 401


async def test_login_unknown_email(client):
    response = await client.post(
        "/auth/login",
        json={"email": "nobody@test.com", "password": "password123"},
    )
    assert response.status_code == 401


async def test_login_invalid_email(client):
    response = await client.post(
        "/auth/login",
        json={"email": "not-an-email", "password": "password123"},
    )
    assert response.status_code == 422


async def test_login_short_password(client):
    response = await client.post(
        "/auth/login",
        json={"email": "user@test.com", "password": "short"},
    )
    assert response.status_code == 422


# POST /auth/change-password

async def test_change_password_success(client, plain_user, auth_headers):
    response = await client.post(
        "/auth/change-password",
        json={"old_password": "password123", "new_password": "newpassword123"},
        headers=auth_headers(plain_user),
    )
    assert response.status_code == 204

    # the new password works
    ok = await client.post(
        "/auth/login",
        json={"email": plain_user.email, "password": "newpassword123"},
    )
    assert ok.status_code == 200

    # the old password no longer works
    stale = await client.post(
        "/auth/login",
        json={"email": plain_user.email, "password": "password123"},
    )
    assert stale.status_code == 401


async def test_change_password_wrong_old_password(client, plain_user, auth_headers):
    response = await client.post(
        "/auth/change-password",
        json={"old_password": "wrongpassword", "new_password": "newpassword123"},
        headers=auth_headers(plain_user),
    )
    assert response.status_code == 401


async def test_change_password_unauthenticated(client):
    response = await client.post(
        "/auth/change-password",
        json={"old_password": "password123", "new_password": "newpassword123"},
    )
    assert response.status_code == 401


# POST /auth/reset

async def _make_reset_token(db_session, user_id, *, token, minutes=10):
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    reset = PasswordResetToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        used=False,
    )
    db_session.add(reset)
    await db_session.commit()
    return reset


async def test_reset_password_success(client, db_session, plain_user):
    await _make_reset_token(db_session, plain_user.id, token="valid-reset-token")

    response = await client.post(
        "/auth/reset",
        json={"token": "valid-reset-token", "new_password": "resetpassword123"},
    )
    assert response.status_code == 204

    # the new password works
    ok = await client.post(
        "/auth/login",
        json={"email": plain_user.email, "password": "resetpassword123"},
    )
    assert ok.status_code == 200


async def test_reset_password_invalid_token(client):
    response = await client.post(
        "/auth/reset",
        json={"token": "does-not-exist", "new_password": "resetpassword123"},
    )
    assert response.status_code == 401


async def test_reset_password_expired_token(client, db_session, plain_user):
    await _make_reset_token(
        db_session, plain_user.id, token="expired-reset-token", minutes=-10
    )

    response = await client.post(
        "/auth/reset",
        json={"token": "expired-reset-token", "new_password": "resetpassword123"},
    )
    assert response.status_code == 401

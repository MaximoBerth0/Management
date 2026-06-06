"""
the user module test evaluates the following:

- Happy path      - normal expected behavior
- Validation      - bad input, missing fields
- Auth/Permission - unauthorized, forbidden
- Edge cases      - duplicates, not found, etc.

Fixtures and helpers come from integration/conftest.py:
- `admin_user`  : user with the admin role (all permissions)
- `plain_user`  : authenticated user with no role / no permissions
- `auth_headers`: builds the Authorization header for a user
"""

# POST /users/register

async def test_register_user(client):
    response = await client.post(
        "/users/register",
        json={
            "email": "newuser@test.com",
            "username": "newuser",
            "password": "password123",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "newuser@test.com"
    assert body["username"] == "newuser"
    assert body["is_active"] is True
    assert "id" in body
    assert "hashed_password" not in body
    assert "password" not in body


async def test_register_user_duplicate_email(client):
    payload = {
        "email": "dupe@test.com",
        "username": "dupe",
        "password": "password123",
    }
    first = await client.post("/users/register", json=payload)
    assert first.status_code == 201

    second = await client.post(
        "/users/register",
        json={**payload, "username": "dupe2"},
    )
    assert second.status_code == 409


async def test_register_user_invalid_email(client):
    response = await client.post(
        "/users/register",
        json={
            "email": "not-an-email",
            "username": "baduser",
            "password": "password123",
        },
    )
    assert response.status_code == 422


async def test_register_user_short_password(client):
    response = await client.post(
        "/users/register",
        json={
            "email": "shortpw@test.com",
            "username": "shortpw",
            "password": "short",
        },
    )
    assert response.status_code == 422


async def test_register_user_missing_fields(client):
    response = await client.post(
        "/users/register",
        json={"email": "missing@test.com"},
    )
    assert response.status_code == 422

# PUT users/me 

async def test_update_profile(client, employee_user, auth_headers):
    response = await client.put(
        "/users/me",
        json={"username": "updated_name"},
        headers=auth_headers(employee_user),
    )
    assert response.status_code == 200
    assert response.json()["username"] == "updated_name"

# GET users/{user_id}

async def test_get_user_by_id(client, admin_user, client_user, auth_headers):
    response = await client.get(
        f"/users/{client_user.id}", headers=auth_headers(admin_user)
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == client_user.id
    assert body["email"] == client_user.email


async def test_get_user_by_id_not_found(client, admin_user, auth_headers):
    response = await client.get(
        "/users/999999", headers=auth_headers(admin_user)
    )
    assert response.status_code == 404


async def test_get_user_by_id_forbidden(client, client_user, auth_headers):
    response = await client.get(
        f"/users/{client_user.id}", headers=auth_headers(client_user)
    )
    assert response.status_code == 403


# GET users/email/{email}

async def test_get_user_by_email(client, admin_user, client_user, auth_headers):
    response = await client.get(
        f"/users/email/{client_user.email}", headers=auth_headers(admin_user)
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == client_user.id
    assert body["email"] == client_user.email


async def test_get_user_by_email_not_found(client, admin_user, auth_headers):
    response = await client.get(
        "/users/email/no@gmail.com", headers=auth_headers(admin_user)
    )
    assert response.status_code == 404


async def test_get_user_by_email_forbidden(client, client_user, auth_headers):
    response = await client.get(
        f"/users/email/{client_user.email}", headers=auth_headers(client_user)
    )
    assert response.status_code == 403


# GET users/list

async def test_list_users(client, admin_user, auth_headers):
    response = await client.get("/users/list", headers=auth_headers(admin_user))
    assert response.status_code == 200

async def test_list_users_forbidden(client, client_user, auth_headers):
    response = await client.get("/users/list", headers=auth_headers(client_user))
    assert response.status_code == 403


# PATCH users/{user_id}/enable

async def test_enable_user(client, employee_user, admin_user, auth_headers):
    response = await client.patch(f"/users/{employee_user.id}/enable", headers=auth_headers(admin_user))
    assert response.status_code == 200

async def test_enable_user_forbidden(client, client_user, auth_headers):
    response = await client.patch(
        f"/users/{client_user.id}/enable", headers=auth_headers(client_user)
    )
    assert response.status_code == 403


# PATCH users/{user_id}/disable

async def test_disable_user(client, employee_user, admin_user, auth_headers):
    response = await client.patch(
        f"/users/{employee_user.id}/disable-account",
        json={"reason": "Policy violation"},
        headers=auth_headers(admin_user),
    )
    assert response.status_code == 200

async def test_disable_user_forbidden(client, client_user, auth_headers):
    response = await client.patch(
        f"/users/{client_user.id}/disable-account", headers=auth_headers(client_user)
    )
    assert response.status_code == 403
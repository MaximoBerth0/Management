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

async def test_list_users(client, admin_user, auth_headers):
    response = await client.get("/users/list", headers=auth_headers(admin_user))
    assert response.status_code == 200

async def test_list_users_forbidden(client, client_user, auth_headers):
    response = await client.get("/users/list", headers=auth_headers(client_user))
    assert response.status_code == 403
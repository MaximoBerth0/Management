import pytest
from app.rbac.models.main_model import Role
from app.users.models import User
from app.core.security.passwords import hash_password


@pytest.mark.asyncio
async def test_create_product_without_permission(client, db_session):

    role = Role(name="basic_user")
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)

    user = User(
        username="testuser",
        email="test@test.com",
        hashed_password=hash_password("fj8f835jfefue9df"),
    )

    user.roles.append(role)

    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        "/auth/login",
        json={
            "email": "test@test.com",
            "password": "fj8f835jfefue9df"
        }
    )

    assert response.status_code == 200, response.json()

    token = response.json()["access_token"]

    response = await client.post(
        "inventory/products",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "new_product",
            "sku": "SKU-123"
        }
    )

    assert response.status_code == 403




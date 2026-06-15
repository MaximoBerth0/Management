"""
docker compose -f docker-compose-test.yml up -d test-db
pytest integration/ -v
docker compose -f docker-compose-test.yml down test-db
"""

import os

# environment variables — must be set before any app import
os.environ["ENV"] = "test"
os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:password@localhost:5432/test_db"
os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-characters-long"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "15"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"
os.environ["CORS_ALLOW_ORIGINS"] = '["http://test"]'
os.environ["AWS_REGION"] = "us-east-1"
os.environ["AWS_ACCESS_KEY_ID"] = "test-access-key-id"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test-secret-access-key"
os.environ["SENDER_EMAIL"] = "no-reply@test"
os.environ["APP_BASE_URL"] = "http://test"

# clear settings cache so test env vars take effect
from app.core.config import get_settings

get_settings.cache_clear()

# model imports — so Base.metadata knows about every table
import app.auth.model
import app.inventory.models.category
import app.inventory.models.location
import app.inventory.models.product
import app.inventory.models.reservation
import app.inventory.models.stock
import app.orders.models.order
import app.rbac.models.permission
import app.rbac.models.role
import app.rbac.models.role_permission
import app.rbac.models.user_role
import app.users.model
import pytest
import pytest_asyncio
from app.core.constants.inventory_permissions import INVENTORY_PERMISSIONS
from app.core.constants.order_permissions import ORDER_PERMISSIONS
from app.core.constants.system_permissions import SYSTEM_PERMISSIONS
from app.core.constants.system_roles import SYSTEM_ROLES
from app.core.constants.user_permissions import USER_PERMISSIONS
from app.core.security.passwords import hash_password
from app.core.security.tokens import create_access_token
from app.database.base import Base
from app.database.session import get_session
from app.main import app
from app.rbac.models.permission import Permission
from app.rbac.models.role import Role
from app.rbac.models.role_permission import role_permissions
from app.rbac.models.user_role import user_roles
from app.users.model import User
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)


# engine + session factory
#
# NullPool: pytest-asyncio runs each test on a fresh event loop, but pooled
# asyncpg connections are bound to the loop that created them. Reusing a pooled
# connection on a later test's loop raises "attached to a different loop", so we
# disable pooling and open a new connection per test.

engine = create_async_engine(os.environ["DATABASE_URL"], poolclass=NullPool)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

# db_session 
# One connection per test. The schema is created and committed, then a single
# OUTER transaction is opened and rolled back at the end.

@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with engine.connect() as conn:
        # create schema and commit it so it survives the outer-transaction rollback
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()

        outer = await conn.begin()

        session = AsyncSession(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        yield session

        await session.close()
        await outer.rollback()        # discard everything the test wrote
        await conn.run_sync(Base.metadata.drop_all)
        await conn.commit()



# seeded — inserts all permissions and roles from constants into test DB

@pytest_asyncio.fixture
async def seeded(db_session):
    all_codes = list(
        set(SYSTEM_PERMISSIONS + INVENTORY_PERMISSIONS + USER_PERMISSIONS + ORDER_PERMISSIONS)
    )

    # insert all permissions
    perm_map: dict[str, Permission] = {}
    for code in all_codes:
        perm = Permission(code=code, name=code, description=code)
        db_session.add(perm)
        perm_map[code] = perm

    await db_session.commit()

    for perm in perm_map.values():
        await db_session.refresh(perm)

    # insert roles and wire their permissions
    role_map: dict[str, Role] = {}
    for role_name, codes in SYSTEM_ROLES.items():
        role = Role(name=role_name)
        db_session.add(role)
        await db_session.commit()
        await db_session.refresh(role)
        role_map[role_name] = role

        for code in codes:
            perm = perm_map.get(code)
            if perm is None:
                continue
            await db_session.execute(
                role_permissions.insert().values(
                    role_id=role.id,
                    permission_id=perm.id,
                )
            )

    await db_session.commit()
    return {"permissions": perm_map, "roles": role_map}

# client — HTTP client wired to the test DB session

@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_session] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

# Internal helpers (not fixtures)

async def _make_user(
    db_session,
    *,
    email: str,
    username: str,
    password: str = "password123",
    is_active: bool = True,
) -> User:
    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
        is_active=is_active,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def _assign_role(db_session, *, user_id: int, role_id: int) -> None:
    await db_session.execute(
        user_roles.insert().values(user_id=user_id, role_id=role_id)
    )
    await db_session.commit()
    # the link was inserted via a Core statement, so the ORM's cached User in
    # the identity map still has an empty `roles` collection. Reload it so the
    # request (which reuses this same session) sees roles/permissions.
    user = await db_session.get(User, user_id)
    if user is not None:
        await db_session.refresh(user, ["roles"])


# user fixtures

@pytest_asyncio.fixture
async def admin_user(db_session, seeded):
    """User with the admin role — has all permissions."""
    user = await _make_user(db_session, email="admin@test.com", username="admin")
    await _assign_role(db_session, user_id=user.id, role_id=seeded["roles"]["admin"].id)
    return user


@pytest_asyncio.fixture
async def employee_user(db_session, seeded):
    """User with the employee role."""
    user = await _make_user(db_session, email="employee@test.com", username="employee")
    await _assign_role(db_session, user_id=user.id, role_id=seeded["roles"]["employee"].id)
    return user


@pytest_asyncio.fixture
async def client_user(db_session, seeded):
    """User with the client role — no permissions."""
    user = await _make_user(db_session, email="client@test.com", username="client")
    await _assign_role(db_session, user_id=user.id, role_id=seeded["roles"]["client"].id)
    return user


@pytest_asyncio.fixture
async def plain_user(db_session):
    """User with no role at all — useful for 401 vs 403 distinction."""
    user = await _make_user(db_session, email="plain@test.com", username="plain")
    return user

# auth_headers - request this fixture, then call it inline: auth_headers(user)
@pytest.fixture
def auth_headers():
    def _build(user: User) -> dict:
        token = create_access_token(user.id)
        return {"Authorization": f"Bearer {token}"}

    return _build


# entity builders — request the fixture, then call it inline with the acting
# user, e.g. `await make_product(admin_user, sku="SKU-2")`. They go through the
# API so the same permission/validation path the tests exercise is used.

@pytest.fixture
def make_category(client, auth_headers):
    async def _make(user: User, name: str = "tools", description: str = "cat") -> int:
        response = await client.post(
            "/inventory/categories",
            headers=auth_headers(user),
            json={"name": name, "description": description},
        )
        assert response.status_code == 201
        return response.json()["id"]

    return _make


@pytest.fixture
def make_product(client, auth_headers, make_category):
    async def _make(
        user: User,
        name: str = "widget",
        sku: str = "SKU-1",
        category_id: int | None = None,
    ) -> int:
        if category_id is None:
            category_id = await make_category(user)
        response = await client.post(
            "/inventory/products",
            headers=auth_headers(user),
            json={"name": name, "sku": sku, "category_id": category_id},
        )
        assert response.status_code == 201
        return response.json()["id"]

    return _make


@pytest.fixture
def make_location(client, auth_headers):
    async def _make(
        user: User,
        name: str = "warehouse",
        city: str = "metropolis",
        address: str = "123 st",
    ) -> int:
        response = await client.post(
            "/inventory/locations",
            headers=auth_headers(user),
            json={"name": name, "city": city, "address": address},
        )
        assert response.status_code == 201
        return response.json()["id"]

    return _make


@pytest.fixture
def make_stock(client, auth_headers, make_product, make_location):
    async def _make(
        user: User,
        product_id: int | None = None,
        location_id: int | None = None,
        quantity: int = 10,
        reorder_point: int = 2,
    ) -> dict:
        if product_id is None:
            product_id = await make_product(user)
        if location_id is None:
            location_id = await make_location(user)
        response = await client.post(
            "/inventory/new",
            headers=auth_headers(user),
            json={
                "location_id": location_id,
                "product_id": product_id,
                "quantity": quantity,
                "reorder_point": reorder_point,
            },
        )
        assert response.status_code == 201
        body = response.json()
        return {
            "stock_id": body["id"],
            "product_id": product_id,
            "location_id": location_id,
            "quantity": body["quantity"],
        }

    return _make


@pytest.fixture
def make_order(client, auth_headers):
    async def _make(user: User) -> int:
        response = await client.post(
            "/orders/",
            headers=auth_headers(user),
        )
        assert response.status_code == 201
        return response.json()["id"]
    return _make


@pytest.fixture
def make_order_item(client, auth_headers, make_order, make_product):
    async def _make(
        user: User,
        order_id: int | None = None,
        product_id: int | None = None,
        quantity: int = 1,
    ) -> dict:
        if order_id is None:
            order_id = await make_order(user)
        if product_id is None:
            product_id = await make_product(user)
        response = await client.post(
            f"/orders/{order_id}/items",
            headers=auth_headers(user),
            json={"product_id": product_id, "quantity": quantity},
        )
        assert response.status_code == 200
        return {
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
        }
    return _make
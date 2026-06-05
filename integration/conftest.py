import os

# Set test configuration before importing anything that reads settings.
# These override any values from a local .env so tests stay self-contained.
os.environ["ENV"] = "test"
os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-characters-long"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "15"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"
os.environ["CORS_ALLOW_ORIGINS"] = '["http://test"]'

from app.core.config import get_settings

get_settings.cache_clear()

import pytest_asyncio
from app.database.base import Base
from app.database.session import get_session
from app.main import app
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# async engine

DATABASE_URL = "sqlite+aiosqlite://"

engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


# session fixture


@pytest_asyncio.fixture(scope="function")
async def db_session():

    async with engine.connect() as conn:
        async with conn.begin():
            await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()

    async with engine.connect() as conn:
        async with conn.begin():
            await conn.run_sync(Base.metadata.drop_all)


# async client


@pytest_asyncio.fixture
async def client(db_session):

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_session] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

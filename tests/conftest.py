import pytest
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import StaticPool

from app.database.base import Base


# DB engine (SQLite async)

DATABASE_URL = "sqlite+aiosqlite://"

engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


# db session

@pytest.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:   # type: ignore
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()

    async with engine.begin() as conn:   # type: ignore
        await conn.run_sync(Base.metadata.drop_all)


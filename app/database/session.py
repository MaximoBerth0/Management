from typing import AsyncGenerator
from sqlalchemy import text 
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import settings

# engine with connection pooling
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    future=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING,

    # connection timeouts (asyncpg specific)
    connect_args={
        "timeout": settings.DB_CONNECT_TIMEOUT,        # connection timeout
        "command_timeout": settings.DB_COMMAND_TIMEOUT, # query timeout
        "server_settings": {
            "statement_timeout": str(settings.DB_STATEMENT_TIMEOUT),  # PostgreSQL timeout
        },
    },
)

# session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# dependency for FastAPI
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# lifecycle management
async def startup() -> None:
    """Test database connection on startup"""
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))

async def shutdown() -> None:
    """Dispose engine on shutdown"""
    await engine.dispose()
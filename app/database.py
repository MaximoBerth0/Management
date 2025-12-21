from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

Base = declarative_base()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
)

async_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_db():
    async with async_session() as session:
        yield session

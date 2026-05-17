from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import AsyncSessionLocal


class UnitOfWork:
    def __init__(self):
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> AsyncSession:
        self.session = AsyncSessionLocal()
        return self.session

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            await self.session.rollback()
        else:
            await self.session.commit()

        await self.session.close()




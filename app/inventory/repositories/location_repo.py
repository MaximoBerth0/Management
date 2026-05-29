from app.inventory.models.location import Location
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class LocationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # used by stock
    async def get_location(self, location_id: int) -> Location | None:
        stmt = select(Location).where(Location.id == location_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

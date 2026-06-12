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

    async def list_locations(self) -> list[Location]:
        stmt = select(Location).order_by(Location.id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> Location | None:
        stmt = select(Location).where(Location.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_location(self, name: str, city: str, address: str) -> Location:
        location = Location(name=name, city=city, address=address)
        self.db.add(location)
        await self.db.commit()
        await self.db.refresh(location)
        return location

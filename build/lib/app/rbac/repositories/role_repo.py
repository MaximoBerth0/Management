from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.rbac.models import Role


class RoleRepository:
    def __init__ (self, db:AsyncSession):
        self.db = db

    async def get_all(self) -> list[Role]:
        stmt = select(Role)
        result = await self.db.scalars(stmt)
        return result.all()
    
    async def get_by_id(self, role_id: int) -> Role | None:
        stmt = select(Role).where(Role.id == role_id)
        result = await self.db.scalars(stmt)
        return result.first()

    async def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name)
        result = await self.db.scalars(stmt)
        return result.first()

    async def create(self, role: Role) -> Role:
        self.db.add(role)
        await self.db.flush()
        return role

    async def get_or_create(self, name: str) -> Role:
        role = await self.get_by_name(name)
        if role:
            return role

        role = Role(name=name)
        self.db.add(role)
        await self.db.flush()
        return role

    async def update(self, role: Role) -> Role:
        await self.db.flush()
        return role

    async def delete(self, role: Role) -> None:
        await self.db.delete(role)
        await self.db.flush()


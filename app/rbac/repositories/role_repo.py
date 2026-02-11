from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.rbac.models.main_model import Role


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Role]:
        stmt = select(Role)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def get_by_id(self, role_id: int) -> Role | None:
        stmt = select(Role).where(Role.id == role_id)
        result = await self.db.scalars(stmt)
        return result.first()

    async def get_by_code(self, code: str) -> Role | None:
        stmt = select(Role).where(Role.code == code)
        result = await self.db.scalars(stmt)
        return result.first()

    async def create(self, role: Role) -> Role:
        self.db.add(role)
        await self.db.flush()
        return role

    async def delete(self, role: Role) -> None:
        await self.db.delete(role)

#    async def get_user_with_roles_and_permissions(self):




from app.rbac.models import UserRole
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRoleRepository:
    def __init__(self, db:AsyncSession):
        self.db = db 

    async def get_by_user(self, user_id: int) -> list[UserRole]:
        stmt = select(UserRole).where(UserRole.user_id == user_id)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def get(self, user_id: int, role_id: int) -> UserRole | None:
        stmt = select(UserRole).where(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id,
            )
        result = await self.db.scalars(stmt)
        return result.first()

    async def add(self, user_id: int, role_id: int) -> UserRole:
        ur = UserRole(
            user_id=user_id,
            role_id=role_id,
        )
        self.db.add(ur)
        await self.db.flush()
        return ur

    async def delete(self, user_role: UserRole) -> None:
        await self.db.delete(user_role)



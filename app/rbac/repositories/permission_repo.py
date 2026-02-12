from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.rbac.models.main_model import Permission


class PermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Permission]:
        stmt = select(Permission)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def get_by_id(self, permission_id: int) -> Permission | None:
        stmt = select(Permission).where(Permission.id == permission_id)
        result = await self.db.scalars(stmt)
        return result.first()

    async def get_by_code(self, code: str) -> Permission | None:
        stmt = select(Permission).where(Permission.code == code)
        result = await self.db.scalars(stmt)
        return result.first()

    async def get_by_name(self, name: str) -> Permission | None:
        stmt = select(Permission).where(Permission.name == name)
        result = await self.db.scalars(stmt)
        return result.first()

    async def create(self, permission: Permission) -> Permission:
        self.db.add(permission)
        await self.db.flush()
        return permission

    async def delete(self, permission: Permission) -> None:
        await self.db.delete(permission)

    async def user_has_permission(
            self,
            user_id: int,
            permission_id: int,
    ) -> bool:
        stmt = (
            select(RolePermission.role_id)
            .join(
                UserRole,
                UserRole.role_id == RolePermission.role_id,
            )
            .where(
                UserRole.user_id == user_id,
                RolePermission.permission_id == permission_id,
            )
            .limit(1)
        )

        result = await self.db.scalar(stmt)
        return result is not None



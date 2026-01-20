from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.rbac.models import Permission, Role, RolePermission


class RolePermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_role(self, role_id: int) -> list[RolePermission]:
        stmt = select(RolePermission).where(RolePermission.role_id == role_id)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def get(self, role_id: int, permission_id: int) -> RolePermission | None:
        stmt = select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
        result = await self.db.scalars(stmt)
        return result.first()

    async def add(self, role_id: int, permission_id: int) -> RolePermission:
        rp = RolePermission(
            role_id=role_id,
            permission_id=permission_id,
        )
        self.db.add(rp)
        await self.db.flush()
        return rp

    async def assign(self, role: Role, permission: Permission) -> RolePermission:
        rp = await self.get(role.id, permission.id)
        if rp:
            return rp

        return await self.add(
            role_id=role.id,
            permission_id=permission.id,
        )

    async def delete(self, role_permission: RolePermission) -> None:
        await self.db.delete(role_permission)



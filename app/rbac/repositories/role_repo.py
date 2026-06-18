import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.rbac.models.role import Role
from app.rbac.models.role_permission import role_permissions
from app.rbac.models.user_role import user_roles
from app.users.model import User


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Role]:
        stmt = select(Role)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def get_by_id(self, role_id: uuid.UUID) -> Role | None:
        stmt = (
            select(Role)
            .where(Role.id == role_id)
            .options(selectinload(Role.permissions))
        )
        result = await self.db.scalars(stmt)
        return result.first()

    async def get_by_code(self, code: str) -> Role | None:
        stmt = select(Role).where(Role.code == code)
        result = await self.db.scalars(stmt)
        return result.first()

    async def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name)
        result = await self.db.scalars(stmt)
        return result.first()

    async def create(self, role: Role) -> Role:
        self.db.add(role)
        await self.db.flush()
        # load the (empty) permissions collection so response serialization
        # doesn't trigger a lazy load outside the async greenlet context
        await self.db.refresh(role, ["permissions"])
        return role

    async def get_or_create(self, name: str, **kwargs) -> Role:
        """this is for bootstraps"""
        role = await self.get_by_name(name)
        if role:
            return role
        return await self.create(Role(name=name, **kwargs))

    async def delete(self, role: Role) -> None:
        await self.db.delete(role)

    # associations

    async def user_has_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        stmt = (
            select(user_roles.c.user_id)
            .where(
                user_roles.c.user_id == user_id,
                user_roles.c.role_id == role_id,
            )
            .limit(1)
        )

        result = await self.db.scalar(stmt)
        return result is not None

    async def add_role_to_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> None:
        stmt = user_roles.insert().values(
            user_id=user_id,
            role_id=role_id,
        )
        await self.db.execute(stmt)

    async def remove_role_from_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> None:
        stmt = delete(user_roles).where(
            user_roles.c.user_id == user_id,
            user_roles.c.role_id == role_id,
        )
        await self.db.execute(stmt)

    async def role_has_permission(self, role_id: uuid.UUID, permission_id: uuid.UUID) -> bool:
        stmt = (
            select(role_permissions.c.role_id)
            .where(
                role_permissions.c.role_id == role_id,
                role_permissions.c.permission_id == permission_id,
            )
            .limit(1)
        )

        result = await self.db.scalar(stmt)
        return result is not None

    async def add_permission_to_role(self, role_id: uuid.UUID, permission_id: uuid.UUID) -> None:
        stmt = role_permissions.insert().values(
            role_id=role_id,
            permission_id=permission_id,
        )
        await self.db.execute(stmt)

    async def remove_permission_from_role(
        self, role_id: uuid.UUID, permission_id: uuid.UUID
    ) -> None:
        stmt = delete(role_permissions).where(
            role_permissions.c.role_id == role_id,
            role_permissions.c.permission_id == permission_id,
        )
        await self.db.execute(stmt)

    # used by ensure_permission() avoiding N+1 queries
    async def get_user_with_roles_and_permissions(
        self,
        user_id: uuid.UUID,
    ):
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

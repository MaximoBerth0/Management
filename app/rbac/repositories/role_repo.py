from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.rbac.models.main_model import Role
from app.users.models import User
from app.rbac.models.tables import user_roles, role_permissions


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

    async def get_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name)
        result = await self.db.scalars(stmt)
        return result.first()

    async def create(self, role: Role) -> Role:
        self.db.add(role)
        await self.db.flush()
        return role

    async def delete(self, role: Role) -> None:
        await self.db.delete(role)

# associations

    async def user_has_role(self, user_id: int, role_id: int) -> bool:
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

    async def add_role_to_user(self, user_id: int, role_id: int) -> None:
        stmt = user_roles.insert().values(
            user_id=user_id,
            role_id=role_id,
        )
        await self.db.execute(stmt)

    async def remove_role_from_user(self, user_id: int, role_id: int) -> None:
        stmt = (
            delete(user_roles)
            .where(
                user_roles.c.user_id == user_id,
                user_roles.c.role_id == role_id,
            )
        )
        await self.db.execute(stmt)

    async def role_has_permission(self, role_id: int, permission_id: int) -> bool:
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

    async def add_permission_to_role(self, role_id: int, permission_id: int) -> None:
        stmt = role_permissions.insert().values(
            role_id=role_id,
            permission_id=permission_id,
        )
        await self.db.execute(stmt)

    async def remove_permission_from_role(self, role_id: int, permission_id: int) -> None:
        stmt = (
            delete(role_permissions)
            .where(
                role_permissions.c.role_id == role_id,
                role_permissions.c.permission_id == permission_id,
            )
        )
        await self.db.execute(stmt)


    async def get_user_with_roles_and_permissions(
            self,
            user_id: int,
    ):
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.roles)
                .selectinload(Role.permissions)
            )
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()






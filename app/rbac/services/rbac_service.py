from app.core.unit_of_work import UnitOfWork
from app.rbac.models import Role
from app.rbac.repositories.permission_repo import PermissionRepository
from app.rbac.repositories.role_permission_repo import RolePermissionRepository
from app.rbac.repositories.role_repo import RoleRepository
from app.rbac.repositories.user_role_repo import UserRoleRepository
from app.shared.exceptions import (
    PermissionAlreadyAssignedToRole,
    PermissionNotFound,
    RoleAlreadyAssignedToUser,
    RoleAlreadyExists,
    RoleNotFound,
    RolePermissionNotFound,
    UserRoleNotFound,
    PermissionDenied
)


class RBACService:
    def __init__(
        self,
        role_repo: RoleRepository,
        permission_repo: PermissionRepository,
        user_role_repo: UserRoleRepository,
        role_permission_repo: RolePermissionRepository,
        uow: UnitOfWork,
    ):
        self.role_repo = role_repo
        self.permission_repo = permission_repo
        self.user_role_repo = user_role_repo
        self.role_permission_repo = role_permission_repo
        self.uow = uow

#roles
    async def create_role(self, name: str):
        async with self.uow as uow:
            role_repo = RoleRepository(uow.session)

            if await role_repo.get_by_name(name):
                raise RoleAlreadyExists()

            role = Role(name=name)
            await role_repo.create(role)

            return role

    async def delete_role(self, role_id: int):
        async with self.uow:
            role = await self.role_repo.get_by_id(role_id)
            if not role:
                raise RoleNotFound()

            await self.role_repo.delete(role)

    async def update_role(self, role_id: int, name: str) -> Role:
        async with self.uow:
            role = await self.role_repo.get_by_id(role_id)
            if not role:
                raise RoleNotFound()

            existing = await self.role_repo.get_by_name(name)
            if existing and existing.id != role_id:
                raise RoleAlreadyExists()

            role.name = name
            return role

    async def list_roles(self):
        return self.role_repo.get_all()

#role-user
    async def assign_role_to_user(self, user_id: int, role_id: int):
        async with self.uow:
            role = await self.role_repo.get_by_id(role_id)
            if not role:
                raise RoleNotFound()

            existing = await self.user_role_repo.get(user_id, role_id)
            if existing:
                raise RoleAlreadyAssignedToUser()

            await self.user_role_repo.add(user_id, role_id)

    async def remove_role_from_user(self, user_id: int, role_id: int):
        async with self.uow:
            user_role = await self.user_role_repo.get(user_id, role_id)
            if not user_role:
                raise UserRoleNotFound()

            await self.user_role_repo.delete(user_role)

#role-permission
    async def add_permission_to_role(self, role_id: int, permission_id: int):
        async with self.uow:
            role = await self.role_repo.get_by_id(role_id)
            if not role:
                raise RoleNotFound()

            permission = await self.permission_repo.get_by_id(permission_id)
            if not permission:
                raise PermissionNotFound()

            existing = await self.role_permission_repo.get(role_id, permission_id)
            if existing:
                raise PermissionAlreadyAssignedToRole()

            await self.role_permission_repo.add(role_id, permission_id)

    async def remove_permission_from_role(self, role_id: int, permission_id: int):
        async with self.uow:
            role_permission = await self.role_permission_repo.get(role_id, permission_id)
            if not role_permission:
                raise RolePermissionNotFound()

            await self.role_permission_repo.delete(role_permission)

#for dependencies
    async def user_has_permission(
            self,
            user_id: int,
            permission_id: int,
    ) -> bool:
        user_roles = await self.user_role_repo.get_by_user(user_id)
        if not user_roles:
            return False

        for ur in user_roles:
            rp = await self.role_permission_repo.get(
                role_id=ur.role_id,  # 👈 ACÁ ESTÁ LA CLAVE
                permission_id=permission_id,
            )
            if rp:
                return True

        return False

    async def require_permission(
            self,
            user_id: int,
            permission_id: int,
    ) -> None:
        if not await self.user_has_permission(user_id, permission_id):
            raise PermissionDenied()





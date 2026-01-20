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
    def create_role(self, name: str):
        with self.uow:
            if self.role_repo.exists_by_name(name):
                raise RoleAlreadyExists()

            role = Role(name=name)
            self.role_repo.create(role)
            return role

    def delete_role(self, role_id: int):
        with self.uow:
            role = self.role_repo.get_by_id(role_id)
            if not role:
                raise RoleNotFound()

            self.role_repo.delete(role)

    def update_role(self, role_id: int, name: str):
        with self.uow:
            role = self.role_repo.get_by_id(role_id)
            if not role:
                raise RoleNotFound()

            role.name = name
            self.role_repo.update(role)
            return role

    def list_roles(self):
        return self.role_repo.get_all()

#role-user
    def assign_role_to_user(self, user_id: int, role_id: int):
        with self.uow:
            role = self.role_repo.get_by_id(role_id)
            if not role:
                raise RoleNotFound()

            existing = self.user_role_repo.get(user_id, role_id)
            if existing:
                raise RoleAlreadyAssignedToUser()

            self.user_role_repo.add(user_id, role_id)

    def remove_role_from_user(self, user_id: int, role_id: int):
        with self.uow:
            user_role = self.user_role_repo.get(user_id, role_id)
            if not user_role:
                raise UserRoleNotFound()

            self.user_role_repo.delete(user_role)

#role-permission
    def add_permission_to_role(self, role_id: int, permission_id: int):
        with self.uow:
            role = self.role_repo.get_by_id(role_id)
            if not role:
                raise RoleNotFound()

            permission = self.permission_repo.get_by_id(permission_id)
            if not permission:
                raise PermissionNotFound()

            existing = self.role_permission_repo.get(role_id, permission_id)
            if existing:
                raise PermissionAlreadyAssignedToRole()

            self.role_permission_repo.add(role_id, permission_id)

    def remove_permission_from_role(self, role_id: int, permission_id: int):
        with self.uow:
            role_permission = self.role_permission_repo.get(role_id, permission_id)
            if not role_permission:
                raise RolePermissionNotFound()

            self.role_permission_repo.delete(role_permission)
from app.database.uow import UnitOfWork
from app.permissions.repositories.permission_repo import PermissionRepository
from app.permissions.repositories.role_permission_repo import RolePermissionRepository
from app.permissions.repositories.role_repo import RoleRepository
from app.permissions.repositories.user_role_repo import UserRoleRepository
from app.shared.exceptions import RoleAlreadyExists


class PermissionsService:
    def __init__(
            self,
            role_repo:RoleRepository,
            permission_repo:PermissionRepository,
            role_permission_repo:RolePermissionRepository,
            user_role_repo:UserRoleRepository,
            uow:UnitOfWork
    ):
        self.role_repo = role_repo
        self.permission_repo = permission_repo
        self.role_permission_repo = role_permission_repo
        self.user_role_repo = user_role_repo
        self.uow = uow 

    def create_role(
        self,
        *,
        name: str,
        is_system: bool = False,
    ):
        with self.uow:
            existing = self.role_repo.get_by_name(name)
            if existing:
                raise RoleAlreadyExists()

            role = self.role_repo.create(
                name=name,
                is_system=is_system
            )

            return role


    
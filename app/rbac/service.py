from app.rbac.models.main_model import Role
from app.rbac.repositories.permission_repo import PermissionRepository
from app.rbac.repositories.role_repo import RoleRepository
from app.rbac.schemas.dto import (
    RoleCreateDTO,
    RoleUpdateDTO,
    RoleResponseDTO,
    AssignRoleToUserDTO,
    AddPermissionToRoleDTO,
    RemoveRoleFromUserDTO,
    RemovePermissionFromRoleDTO,
)
from app.rbac.errors import (
    PermissionAlreadyAssigned,
    PermissionNotFound,
    RoleAlreadyAssignedToUser,
    RoleAlreadyExists,
    RoleNotFound,
    RolePermissionNotFound,
    UserRoleNotFound,
    PermissionDenied,
)


class RBACService:
    def __init__(
        self,
        role_repo: RoleRepository,
        permission_repo: PermissionRepository,
    ):
        self.role_repo = role_repo
        self.permission_repo = permission_repo

    # Roles
    async def create_role(self, data: RoleCreateDTO) -> RoleResponseDTO:
        if await self.role_repo.get_by_name(data.name):
            raise RoleAlreadyExists()

        role = Role(name=data.name, description=data.description)
        await self.role_repo.create(role)
        return RoleResponseDTO.model_validate(role)

    async def update_role(self, role_id: int, data: RoleUpdateDTO) -> RoleResponseDTO:
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise RoleNotFound()

        if data.name:
            existing = await self.role_repo.get_by_name(data.name)
            if existing and existing.id != role_id:
                raise RoleAlreadyExists()
            role.name = data.name

        if data.description is not None:
            role.description = data.description

        return RoleResponseDTO.model_validate(role)

    async def list_roles(self) -> list[RoleResponseDTO]:
        roles = await self.role_repo.get_all()
        return [RoleResponseDTO.model_validate(r) for r in roles]

    # Role-User
    async def assign_role_to_user(self, data: AssignRoleToUserDTO):
        role = await self.role_repo.get_by_id(data.role_id)
        if not role:
            raise RoleNotFound()

        if await self.role_repo.user_has_role(data.user_id, data.role_id):
            raise RoleAlreadyAssignedToUser()

        await self.role_repo.add_role_to_user(data.user_id, data.role_id)

    async def remove_role_from_user(self, data: RemoveRoleFromUserDTO) -> None:
        if not await self.role_repo.user_has_role(data.user_id, data.role_id):
            raise UserRoleNotFound()

        await self.role_repo.remove_role_from_user(data.user_id, data.role_id)

    # Role-Permission
    async def add_permission_to_role(self, role_id: int, data: AddPermissionToRoleDTO):
        role = await self.role_repo.get_by_id(role_id)
        if not role:
            raise RoleNotFound()

        permission = await self.permission_repo.get_by_id(data.permission_id)
        if not permission:
            raise PermissionNotFound()

        if await self.role_repo.role_has_permission(role_id, data.permission_id):
            raise PermissionAlreadyAssigned()

        await self.role_repo.add_permission_to_role(role_id, data.permission_id)

    async def remove_permission_from_role(
        self, role_id: int, data: RemovePermissionFromRoleDTO
    ) -> None:
        if not await self.role_repo.role_has_permission(role_id, data.permission_id):
            raise RolePermissionNotFound()

        await self.role_repo.remove_permission_from_role(role_id, data.permission_id)

    # permission checks
    async def ensure_permission(self, user_id: int, permission_code: str) -> None:
        user = await self.role_repo.get_user_with_roles_and_permissions(user_id)
        if not user:
            raise PermissionDenied()

        has_permission = any(
            permission.code == permission_code
            for role in user.roles
            for permission in role.permissions
        )

        if not has_permission:
            raise PermissionDenied()

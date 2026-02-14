from fastapi import APIRouter, Depends, status

from app.rbac.dependencies import get_rbac_service
from app.rbac.schemas.api import (
    RoleCreateRequest,
    RoleUpdateRequest,
    AddPermissionToRoleRequest,
    RemovePermissionFromRoleRequest,
)
from app.rbac.schemas.dto import RoleCreateDTO, RoleUpdateDTO, AddPermissionToRoleDTO, AssignRoleToUserDTO, RemovePermissionFromRoleDTO, RemoveRoleFromUserDTO
from app.rbac.service import RBACService

router = APIRouter(
    prefix="/rbac",
    tags=["RBAC"],
)

# roles

@router.post(
    "/roles",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("role:create"))],
)
async def create_role(
    data: RoleCreateRequest,
    service: RBACService = Depends(get_rbac_service),
):
    dto = RoleCreateDTO(
        name = data.name,
        description = data.description,
    )
    return await service.create_role(dto)


@router.patch(
    "/roles/{role_id}",
    dependencies=[Depends(require_permission("role:update"))],
)
async def update_role(
    role_id: int,
    data: RoleUpdateRequest,
    service: RBACService = Depends(get_rbac_service),
):
    dto = RoleUpdateDTO(
        name=data.name,
        description=data.description,
    )
    return await service.update_role(role_id, dto)


# Role-Permission

@router.post(
    "/roles/{role_id}/permissions",
    status_code=status.HTTP_201_CREATED,
)
async def assign_permission_to_role(
    role_id: int,
    data: AddPermissionToRoleRequest,
    service: RBACService = Depends(get_rbac_service),
):
    dto = AddPermissionToRoleDTO(
        permission_id=data.permission_id,
    )

    return await service.add_permission_to_role(role_id, dto)


@router.delete(
    "/roles/{role_id}/permissions",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("role:remove_permission"))],
)
async def remove_permission_from_role(
    role_id: int,
    data: RemovePermissionFromRoleRequest,
    service: RBACService = Depends(get_rbac_service),
) -> None:
    dto = RemovePermissionFromRoleDTO(
        permission_id=data.permission_id,
    )

    await service.remove_permission_from_role(
        role_id=role_id,
        data=dto,
    )


#==== ROLE-USER ====

@router.post(
    "/users/{user_id}/roles/{role_id}",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("users:assign_role"))],
)
async def assign_role_to_user(
    user_id: int,
    role_id: int,
    service: RBACService = Depends(get_rbac_service),
):
    dto = AssignRoleToUserDTO(
        user_id=user_id,
        role_id=role_id,
    )

    return await service.assign_role_to_user(dto)


@router.delete(
    "/users/{user_id}/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("users:remove_role"))],
)
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    service: RBACService = Depends(get_rbac_service),
) -> None:
    dto = RemoveRoleFromUserDTO(
        user_id=user_id,
        role_id=role_id,
    )

    await service.remove_role_from_user(dto)

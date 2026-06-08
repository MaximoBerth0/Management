from fastapi import APIRouter, Depends, status

from app.rbac.dependencies import get_rbac_service, require_permission
from app.rbac.models.role import Role
from app.rbac.schemas import (
    AddPermissionToRoleRequest,
    RemovePermissionFromRoleRequest,
    RoleCreateRequest,
    RoleResponse,
    RoleUpdateRequest,
)
from app.rbac.service import RBACService

"""
POST   /rbac/roles                                      - create role
PATCH  /rbac/roles/{role_id}                            - update role
GET    /rbac/roles                                      - list roles

# role-permission
POST   /rbac/roles/{role_id}/permissions               - assign permission to role
DELETE /rbac/roles/{role_id}/permissions               - remove permission from role

# role-user
POST   /rbac/users/{user_id}/roles/{role_id}           - assign role to user
DELETE /rbac/users/{user_id}/roles/{role_id}           - remove role from user
"""

router = APIRouter(
    prefix="/rbac",
    tags=["RBAC"],
)

# roles


@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("roles:create"))],
)
async def create_role(
    data: RoleCreateRequest,
    service: RBACService = Depends(get_rbac_service),
):
    return await service.create_role(
        name=data.name,
        description=data.description,
    )


@router.patch(
    "/roles/{role_id}",
    response_model=RoleResponse,
    dependencies=[Depends(require_permission("roles:update"))],
)
async def update_role(
    role_id: int,
    data: RoleUpdateRequest,
    service: RBACService = Depends(get_rbac_service),
):
    return await service.update_role(
        role_id,
        name=data.name,
        description=data.description,
    )


@router.get(
    "/roles",
    response_model=list[RoleResponse],
    dependencies=[Depends(require_permission("roles:view"))],
)
async def list_roles(
    service: RBACService = Depends(get_rbac_service),
) -> list[Role]:
    return await service.list_roles()


# Role-Permission


@router.post(
    "/roles/{role_id}/permissions",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("role:assign_permission"))],
)
async def assign_permission_to_role(
    role_id: int,
    data: AddPermissionToRoleRequest,
    service: RBACService = Depends(get_rbac_service),
):
    return await service.add_permission_to_role(
        role_id=role_id,
        permission_id=data.permission_id,
    )


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
    await service.remove_permission_from_role(
        role_id=role_id,
        permission_id=data.permission_id,
    )


# ==== ROLE-USER ====


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
    return await service.assign_role_to_user(
        user_id=user_id,
        role_id=role_id,
    )


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
    await service.remove_role_from_user(
        user_id=user_id,
        role_id=role_id,
    )

from fastapi import APIRouter, Depends, status

from app.rbac.dependencies import get_rbac_service, require_permission
from app.rbac.schemas.assign import PermissionAssign
from app.rbac.schemas.role import RoleCreate, RoleUpdate
from app.rbac.service import RBACService

router = APIRouter(
    prefix="/rbac",
    tags=["RBAC"],
)

#==== ROLES ====

@router.post(
    "/roles",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("role:create"))],
)
async def create_role(
    data: RoleCreate,
    service: RBACService = Depends(get_rbac_service),
):
    return await service.create_role(data)

@router.patch(
    "/roles/{role_id}",
    dependencies=[Depends(require_permission("role:update"))],
)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    service: RBACService = Depends(get_rbac_service),
):
    return await service.update_role(role_id, data)

@router.delete(
    "/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("role:delete"))],
)
async def delete_role(
    role_id: int,
    service: RBACService = Depends(get_rbac_service),
) -> None:
    await service.delete_role(role_id)

#==== PERMISSION-ROLE ====

@router.post(
    "/roles/{role_id}/permissions",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("role:assign_permission"))],
)
async def assign_permission_to_role(
    role_id: int,
    data: PermissionAssign,
    service: RBACService = Depends(get_rbac_service),
):
    return await service.add_permission_to_role(
        role_id=role_id,
        data=data,
    )

#==== ROLE-USER ====

@router.post(
    "/users/{user_id}/roles/{role_id}",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("user:assign_role"))],
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

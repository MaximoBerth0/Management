from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.permissions.schemas.permission import PermissionAssign
from app.permissions.schemas.role import RoleCreate, RoleUpdate
from app.permissions.schemas.user_role import AssignRole
from app.permissions.services.permission_auth import PermissionAuthService
from app.permissions.services.permission_service import PermissionService

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
)

@router.get("/roles")
def list_roles(
    current_user = Depends(get_current_user),
    auth: PermissionAuthService = Depends(),
    service: PermissionService = Depends(),
):
    auth.require_permission(current_user.id, "roles:view")
    return service.list_roles()

@router.post("/roles")
def create_role(
    payload: RoleCreate,
    current_user = Depends(get_current_user),
    auth: PermissionAuthService = Depends(),
    service: PermissionService = Depends(),
):
    auth.require_permission(current_user.id, "roles:create")
    return service.create_role(payload)

@router.put("/roles/{role_id}")
def update_role(
    role_id: int,
    payload: RoleUpdate,
    current_user = Depends(get_current_user),
    auth: PermissionAuthService = Depends(),
    service: PermissionService = Depends(),
):
    auth.require_permission(current_user.id, "roles:update")
    return service.update_role(role_id, payload)

@router.delete("/roles/{role_id}")
def delete_role(
    role_id: int,
    current_user = Depends(get_current_user),
    auth: PermissionAuthService = Depends(),
    service: PermissionService = Depends(),
):
    auth.require_permission(current_user.id, "roles:delete")
    return service.delete_role(role_id)

@router.get("/roles/{role_id}/permissions")
def list_role_permissions(
    role_id: int,
    current_user = Depends(get_current_user),
    auth: PermissionAuthService = Depends(),
    service: PermissionService = Depends(),
):
    auth.require_permission(current_user.id, "roles:permissions:view")
    return service.list_role_permissions(role_id)

@router.post("/roles/{role_id}/permissions")
def add_permission_to_role(
    role_id: int,
    payload: PermissionAssign,
    current_user = Depends(get_current_user),
    auth: PermissionAuthService = Depends(),
    service: PermissionService = Depends(),
):
    auth.require_permission(current_user.id, "roles:permissions:update")
    return service.add_permission_to_role(
        role_id=role_id,
        permission_id=payload.permission_id,
    )

@router.delete("/roles/{role_id}/permissions/{permission_id}")
def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    current_user = Depends(get_current_user),
    auth: PermissionAuthService = Depends(),
    service: PermissionService = Depends(),
):
    auth.require_permission(current_user.id, "roles:permissions:update")
    return service.remove_permission_from_role(role_id, permission_id)

@router.get("/users/{user_id}/roles")
def list_user_roles(
    user_id: int,
    current_user = Depends(get_current_user),
    auth: PermissionAuthService = Depends(),
    service: PermissionService = Depends(),
):
    auth.require_permission(current_user.id, "users:roles:view")
    return service.list_user_roles(user_id)

@router.post("/users/{user_id}/roles")
def assign_role_to_user(
    user_id: int,
    payload: AssignRole,
    current_user = Depends(get_current_user),
    auth: PermissionAuthService = Depends(),
    service: PermissionService = Depends(),
):
    auth.require_permission(current_user.id, "users:roles:update")
    return service.assign_role_to_user(user_id, payload.role_id)

@router.delete("/users/{user_id}/roles/{role_id}")
def remove_role_from_user(
    user_id: int,
    role_id: int,
    current_user = Depends(get_current_user),
    auth: PermissionAuthService = Depends(),
    service: PermissionService = Depends(),
):
    auth.require_permission(current_user.id, "users:roles:update")
    return service.remove_role_from_user(user_id, role_id)

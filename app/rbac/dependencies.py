from fastapi import Depends

from app.auth.dependencies import get_current_user
from app.rbac.factory import get_permission_service
from app.rbac.services.permission_service import PermissionService
from app.users.models import User


def require_permission(permission_name: str):
    def dependency(
        current_user: User = Depends(get_current_user),
        service: PermissionService = Depends(get_permission_service),
    ) -> User:
        service.require_permission(current_user.id, permission_name)
        return current_user

    return dependency
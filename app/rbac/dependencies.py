from app.auth.dependencies import get_current_user
from app.users.models import User
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.core.unit_of_work import UnitOfWork
from app.rbac.repositories.permission_repo import PermissionRepository
from app.rbac.repositories.role_repo import RoleRepository
from app.rbac.repositories.role_permission_repo import RolePermissionRepository
from app.rbac.repositories.user_role_repo import UserRoleRepository
from app.rbac.services.rbac_service import RBACService


async def get_rbac_service(
    db: AsyncSession = Depends(get_session),
) -> RBACService:
    uow = UnitOfWork(db)

    return RBACService(
        role_repo=RoleRepository(db),
        permission_repo=PermissionRepository(db),
        user_role_repo=UserRoleRepository(db),
        role_permission_repo=RolePermissionRepository(db),
        uow=uow,
    )


def require_permission(permission_code: str):
    async def dependency(
        current_user: User = Depends(get_current_user),
        service: RBACService = Depends(get_rbac_service),
    ) -> User:
        await service.require_permission(
            user_id=current_user.id,
            permission_code=permission_code,
        )
        return current_user

    return dependency

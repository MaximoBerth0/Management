from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWork
from app.database.session import get_session
from app.rbac.repositories.permission_repo import PermissionRepository
from app.rbac.repositories.role_repo import RoleRepository
from app.rbac.service import RBACService
from app.auth.dependencies import get_current_user
from app.users.models import User


async def get_rbac_service(
    db: AsyncSession = Depends(get_session),
) -> RBACService:
    uow = UnitOfWork()

    return RBACService(
        role_repo=RoleRepository(db),
        permission_repo=PermissionRepository(db),
        uow=uow,
    )


def require_permission(permission_code: str):
    async def dependency(
        current_user: User = Depends(get_current_user),
        service: RBACService = Depends(get_rbac_service),
    ):
        has_permission = await service.user_has_permission(
            user_id=current_user.id,
            permission_code=permission_code,
        )

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )

    return dependency



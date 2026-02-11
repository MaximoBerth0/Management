from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWork
from app.database.session import get_session
from app.rbac.repositories.permission_repo import PermissionRepository
from app.rbac.repositories.role_repo import RoleRepository
from app.rbac.service import RBACService



async def get_rbac_service(
    db: AsyncSession = Depends(get_session),
) -> RBACService:
    uow = UnitOfWork()

    return RBACService(
        role_repo=RoleRepository(db),
        permission_repo=PermissionRepository(db),
        uow=uow,
    )


# def require_permission



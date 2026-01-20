from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.rbac.repositories.role_repo import RoleRepository
from app.rbac.services.permission_service import PermissionService


def get_permission_service(
    db: Session = Depends(get_db),
) -> PermissionService:
    repo = RoleRepository(db)
    return PermissionService(repo)

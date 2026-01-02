from app.permissions.repositories.permission_repo import PermissionRepository
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

"""
this class function indicates whether
a user has a permission, directly or indirectly, through their roles.
"""
class PermissionAuthService:
    def __init__(self, db: Session):
        self.permission_repo = PermissionRepository(db)

    def require_permission(self, user_id: int, permission_code: str) -> None:
        permissions = self.permission_repo.get_permission_codes_by_user(user_id)

        if permission_code not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
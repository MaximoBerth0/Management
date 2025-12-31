from app.permissions.repositories.permission_repo import PermissionRepository
from sqlalchemy.orm import Session

"""
this class function indicates whether
a user has a permission, directly or indirectly, through their roles.
"""
class PermissionAuthService:
    def __init__(self, db: Session):
        self.permission_repo = PermissionRepository(db)

    def user_has_permission(self, user_id: int, permission_code: str) -> bool:
        permissions = self.permission_repo.get_permission_codes_by_user(user_id)
        return permission_code in permissions

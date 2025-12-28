from app.permissions.models import UserRole
from sqlalchemy import select
from sqlalchemy.orm import Session


class UserRoleRepository:
    def __init__(self, db:Session):
        self.db = db 

    def get_by_user(self, user_id: int) -> list[UserRole]:
        stmt = select(UserRole).where(UserRole.user_id == user_id)
        return self.db.scalars(stmt).all()

    def get(self, user_id: int, role_id: int) -> UserRole | None:
        stmt = select(UserRole).where(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id,
            )
        return self.db.scalars(stmt).first()
    
    def add(self, user_id: int, role_id: int) -> UserRole:
        ur = UserRole(
        user_id=user_id,
        role_id=role_id,
            )
        self.db.add(ur)
        return ur
    
    def delete(self, user_role: UserRole) -> None:
        self.db.delete(user_role)



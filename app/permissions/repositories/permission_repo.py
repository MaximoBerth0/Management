from app.permissions.models import Permission
from sqlalchemy import select
from sqlalchemy.orm import Session


class PermissionRepository:
    def __init__(self, db:Session):
        self.db = db

    def get_all(self) -> list[Permission]:
        stmt = select(Permission)
        return self.db.scalars(stmt).all()

    def get_by_id(self, permission_id:int) -> Permission | None:
        stmt = select(Permission).where(Permission.id == permission_id)
        return self.db.scalars(stmt).first()

    def get_by_name(self, name:str) -> Permission | None: 
        stmt = select(Permission).where(Permission.name == name)
        return self.db.scalars(stmt).first()

    def create(self, permission: Permission) -> Permission:
        self.db.add(permission)
        return permission
        
    def delete(self, permission:Permission) -> None:
        self.db.delete(permission)




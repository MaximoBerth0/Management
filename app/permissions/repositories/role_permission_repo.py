from app.permissions.models import RolePermission
from sqlalchemy import select
from sqlalchemy.orm import Session


class RolePermissionRepository:
    def __init__(self, db:Session):
        self.db = db

    def get_by_role(self, role_id:int) -> list[RolePermission]: 
        stmt = select(RolePermission).where(RolePermission.role_id == role_id)
        self.db.scalars(stmt).all()

    def get(self, role_id: int, permission_id: int) -> RolePermission | None:
        stmt = select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
        return self.db.scalars(stmt).first()

    def add(self, role_id: int, permission_id: int) -> RolePermission:
        rp = RolePermission(
            role_id=role_id,
            permission_id=permission_id,
        )
        self.db.add(rp)
        return rp

    def delete(self, role_permission: RolePermission) -> None:
        self.db.delete(role_permission)

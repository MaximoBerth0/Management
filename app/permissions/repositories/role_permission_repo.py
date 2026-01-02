from sqlalchemy import select
from sqlalchemy.orm import Session

from app.permissions.models import Permission, Role, RolePermission


class RolePermissionRepository:
    def __init__(self, db:Session):
        self.db = db

    def get_by_role(self, role_id:int) -> list[RolePermission]: 
        stmt = select(RolePermission).where(RolePermission.role_id == role_id)
        return self.db.scalars(stmt).all()

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
    
    def assign(self, role: Role, permission: Permission) -> RolePermission:
        rp = self.get(role.id, permission.id)
        if rp:
            return rp

        return self.add(
            role_id=role.id,
            permission_id=permission.id,
        )

    def delete(self, role_permission: RolePermission) -> None:
        self.db.delete(role_permission)

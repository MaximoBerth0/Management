from sqlalchemy import select
from sqlalchemy.orm import Session

from app.permissions.models import Role


class RoleRepository:
    def __init__ (self, db:Session):
        self.db = db

    def get_all(self) -> list[Role]:
        stmt = select(Role)
        return self.db.scalars(stmt).all()
    
    def get_by_id(self, role_id: int) -> Role | None:
        stmt = select(Role).where(Role.id == role_id)
        return self.db.scalars(stmt).first()

    def create(self, role: Role) -> Role:
        self.db.add(role)
        return role
    
    def update(self, role: Role) -> Role:
        self.db.add(role)
        return role

    def delete(self, role: Role) -> None:
        self.db.delete(role)

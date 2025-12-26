from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.users.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        return self.db.scalar(stmt)

    def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        stmt = select(User).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()

    def add(self, user: User) -> None:
        self.db.add(user)

    def delete(self, user: User) -> None:
        self.db.delete(user)

    def set_active(self, user: User, is_active: bool) -> None:
        user.is_active = is_active

    def update_fields(self, user: User, data: dict) -> None:
        for field, value in data.items():
            if not hasattr(user, field):
                continue
            setattr(user, field, value)

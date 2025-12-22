from app.auth.security import hash_password
from app.shared.exceptions import (
    UserAlreadyExists,
    UserInactive,
    UserNotFound,
)
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate, UserUpdate
from sqlalchemy.orm import Session


class UserService:
    def __init__(self, db: Session, user_repo: UserRepository):
        self.db = db
        self.user_repo = user_repo

    def create_user(self, data: UserCreate) -> User:
        existing = self.user_repo.get_by_email(data.email)
        if existing:
            raise UserAlreadyExists("Email already registered")

        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
            is_active=True,
        )

        self.user_repo.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.user_repo.list(skip=skip, limit=limit)

    def get_user_by_id(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound("User not found")
        return user

    def update_user(self, user_id: int, data: UserUpdate) -> User:
        user = self.get_user_by_id(user_id)

        update_data = data.model_dump(exclude_unset=True)

        if "email" in update_data:
            existing = self.user_repo.get_by_email(update_data["email"])
            if existing and existing.id != user.id:
                raise UserAlreadyExists("Email already registered")

        self.user_repo.update_fields(user, update_data)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> None:
        user = self.get_user_by_id(user_id)
        self.user_repo.delete(user)
        self.db.commit()

    def disable_user(self, user_id: int) -> User:
        user = self.get_user_by_id(user_id)
        self.user_repo.set_active(user, False)
        self.db.commit()
        self.db.refresh(user)
        return user

    def enable_user(self, user_id: int) -> User:
        user = self.get_user_by_id(user_id)
        self.user_repo.set_active(user, True)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_profile(self, user_id: int) -> User:
        user = self.get_user_by_id(user_id)
        if not user.is_active:
            raise UserInactive("User is inactive")
        return user

    def update_profile(self, user_id: int, data: UserUpdate) -> User:
        user = self.get_profile(user_id)

        update_data = data.model_dump(exclude_unset=True)

        if "email" in update_data:
            existing = self.user_repo.get_by_email(update_data["email"])
            if existing and existing.id != user.id:
                raise UserAlreadyExists("Email already registered")

        self.user_repo.update_fields(user, update_data)
        self.db.commit()
        self.db.refresh(user)
        return user

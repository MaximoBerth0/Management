from app.shared.exceptions import (
    UserAlreadyExists,
    UserInactive,
    UserNotFound,
)
from app.core.security.passwords import hash_password
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def create_user(self, data: UserCreate) -> User:
        if self.user_repo.get_by_email(str(data.email)):
            raise UserAlreadyExists("Email already registered")

        user = User(
            email=str(data.email),
            username=data.username,
            hashed_password=hash_password(data.password),
            is_active=True,
        )
        return self.user_repo.save(user)

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.user_repo.list(skip, limit)

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

        for field, value in update_data.items():
            setattr(user, field, value)

        return self.user_repo.save(user)

    def delete_user(self, user_id: int) -> None:
        user = self.get_user_by_id(user_id)
        self.user_repo.delete(user)

    def disable_user(self, user_id: int) -> User:
        user = self.get_user_by_id(user_id)
        user.is_active = False
        return self.user_repo.save(user)

    def enable_user(self, user_id: int) -> User:
        user = self.get_user_by_id(user_id)
        user.is_active = True
        return self.user_repo.save(user)

    def get_profile(self, user_id: int) -> User:
        user = self.get_user_by_id(user_id)
        if not user.is_active:
            raise UserInactive("User is inactive")
        return user
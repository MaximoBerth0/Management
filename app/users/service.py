from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.passwords import hash_password
from app.users.exceptions import UserAlreadyExists, UserNotFound
from app.users.model import User
from app.users.repository import UserRepository


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)

    async def register_user(self, email: str, username: str, password: str) -> User:
        existing = await self.repo.get_by_email(email)
        if existing:
            raise UserAlreadyExists("User with this email already exists")
        user = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            is_active=True,
        )
        await self.repo.create_user(user)
        return user
    
    async def update_profile(self, current_user: User, data: dict) -> User:
        if not data:
            return current_user
        forbidden_fields = {"id", "is_active", "created_at", "updated_at"}
        safe_data = {k: v for k, v in data.items() if k not in forbidden_fields}
        if not safe_data:
            return current_user
        return await self.repo.update_profile(user=current_user, data=safe_data)
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        limit = min(limit, 100)

        users = await self.repo.list_users(
            skip=skip,
            limit=limit,
        )

        return list(users)

    async def get_user_by_id(
        self,
        user_id: int,
    ) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFound("User not found")

        return user

    async def get_user_by_email(
        self,
        email: str,
    ) -> User:
        user = await self.repo.get_by_email(email)
        if not user:
            raise UserNotFound("User not found")

        return user

    async def enable_account(self, user_id: int) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFound("User not found")

        user.disabled_at = None
        user.disabled_by = None
        user.reason = None

        return await self.repo.enable_account(user)

    async def disable_account(
        self, user_id: int, disabled_by_user_id: int, reason: str
    ) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFound("User not found")

        user.disabled_at = datetime.now(timezone.utc)
        user.disabled_by = disabled_by_user_id
        user.reason = reason

        return await self.repo.disable_account(user)

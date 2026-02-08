from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.passwords import hash_password
from app.shared.exceptions.user_errors import UserAlreadyExists, UserNotFound
from app.shared.exceptions.rbac_errors import PermissionDenied
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)


    async def register_user(self, data: UserCreate) -> User:
        existing = await self.repo.get_by_email(str(data.email))
        if existing:
            raise UserAlreadyExists("User with this email already exists")

        user = User(
            email=str(data.email),
            username=data.username,
            hashed_password=hash_password(data.password),
            is_active=True,
        )

        await self.repo.save(user)
        return user


    async def update_profile(
        self,
        current_user: User,
        data: UserUpdate,
    ) -> User:
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            return current_user

        forbidden_fields = {
            "id",
            "is_active",
            "is_superuser",
            "created_at",
            "updated_at",
        }

        safe_data = {
            field: value
            for field, value in update_data.items()
            if field not in forbidden_fields
        }

        if not safe_data:
            return current_user

        return await self.repo.update(
            user=current_user,
            data=safe_data,
        )


    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        limit = min(limit, 100)

        users = await self.repo.list(
            skip=skip,
            limit=limit,
        )

        return list(users)

    async def get_user(
        self,
        user_id: int,
    ) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFound("User not found")

        return user

    async def set_user_active(
        self,
        current_user: User,
        user_id: int,
        active: bool,
    ) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFound("User not found")

        if user.id == current_user.id:
            raise PermissionDenied("You cannot change your own active status")

        return await self.repo.update(
            user=user,
            data={"is_active": active},
        )




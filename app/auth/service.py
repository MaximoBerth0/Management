from datetime import datetime, timedelta, timezone

from app.core.security.passwords import (
    verify_password,
    hash_password,
    )

from app.core.security.tokens import (create_access_token, generate_refresh_token, generate_reset_token)

from app.shared.exceptions.auth_errors import InvalidCredentials, TokenExpired, TokenInvalid

from app.auth.repositories.refresh_token import RefreshTokenRepository
from app.auth.repositories.password_reset import PasswordResetTokenRepository
from app.users.repository import UserRepository
from app.users.models import User
from app.mail.mailer import Mailer

from app.core.config import settings


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        refresh_repo: RefreshTokenRepository,
        reset_repo: PasswordResetTokenRepository,
        mailer: Mailer,
    ):
        self.user_repo = user_repo
        self.refresh_repo = refresh_repo
        self.reset_repo = reset_repo
        self.mailer = mailer


    async def login(self, email: str, password: str) -> dict:
        user = await self.user_repo.get_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentials("Credentials not valid.")

        access_token = create_access_token(user.id)

        refresh_token = generate_refresh_token()
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        await self.refresh_repo.create(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }


    async def logout(self, refresh_token: str) -> None:
        token = await self.refresh_repo.get_active(refresh_token)

        if not token:
            return

        await self.refresh_repo.revoke(token.id)


    async def refresh_session(self, refresh_token: str) -> dict:
        token = await self.refresh_repo.get_active(refresh_token)

        if not token or token.expires_at < datetime.now(timezone.utc):
            raise TokenExpired("Invalid refresh token.")

        await self.refresh_repo.revoke(token.id)

        new_refresh_token = generate_refresh_token()
        new_expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        await self.refresh_repo.create(
            user_id=token.user_id,
            token=new_refresh_token,
            expires_at=new_expires_at,
        )

        access_token = create_access_token(token.user_id)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }


    async def forgot_password(self, email: str) -> None:
        user = await self.user_repo.get_by_email(email)

        if not user:
            return

        await self.reset_repo.invalidate_all_for_user(user.id)

        token = generate_reset_token()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

        await self.reset_repo.create(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
        )

        await self.mailer.send_reset_email(user.email, token)


    async def reset_password(self, token: str, new_password: str) -> None:
        reset = await self.reset_repo.get_valid(token)

        if not reset:
            raise TokenInvalid("Invalid reset token")

        if reset.expires_at < datetime.now(timezone.utc):
            raise TokenExpired("Reset token expired")

        user = await self.user_repo.get_by_id(int(reset.user_id))

        user.hashed_password = hash_password(new_password)
        await self.user_repo.save(user)

        await self.reset_repo.invalidate(token)
        user_id: int = reset.user_id
        await self.refresh_repo.revoke_all_for_user(user_id)


    async def change_password(
            self,
            current_user: User,
            old_password: str,
            new_password: str,
    ) -> None:
        if not verify_password(old_password, current_user.hashed_password):
            raise InvalidCredentials("Invalid password")

        current_user.hashed_password = hash_password(new_password)
        await self.user_repo.save(current_user)

        await self.refresh_repo.revoke_all_for_user(int(current_user.id))

from datetime import datetime, timedelta, timezone

from app.auth.repositories.password_reset import PasswordResetTokenRepository
from app.auth.repositories.refresh_token import RefreshTokenRepository
from app.core.config import settings
from app.core.security.passwords import (
    hash_password,
    verify_password,
)
from app.core.security.tokens import (
    create_access_token,
    generate_refresh_token,
    generate_reset_token,
)
from app.mail.mailer import Mailer
from app.auth.errors import (
    InvalidCredentials,
    TokenExpired,
    TokenInvalid,
)
from app.auth.schemas.dto import (
    LoginDTO,
    LogoutDTO,
    RefreshSessionDTO,
    ForgotPasswordDTO,
    ResetPasswordDTO,
    ChangePasswordDTO,
    TokenResponseDTO,
)
from app.users.models import User
from app.users.repository import UserRepository


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        refresh_repo: RefreshTokenRepository,
        reset_repo: PasswordResetTokenRepository,
        mailer: Mailer
    ):
        self.user_repo = user_repo
        self.refresh_repo = refresh_repo
        self.reset_repo = reset_repo
        self.mailer = mailer


    async def login(self, data: LoginDTO) -> TokenResponseDTO:
        user = await self.user_repo.get_by_email(data.email)

        if not user or not verify_password(data.password, user.hashed_password):
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

        return TokenResponseDTO(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def logout(self, data: LogoutDTO) -> None:
        token = await self.refresh_repo.get_active(data.refresh_token)

        if not token:
            raise TokenInvalid("token is inactive")

        await self.refresh_repo.revoke(token.id)

    async def refresh_session(self, data: RefreshSessionDTO) -> TokenResponseDTO:
        token = await self.refresh_repo.get_active(data.refresh_token)

        if not token:
            raise TokenExpired("Invalid refresh token.")

        if token.expires_at < datetime.now(timezone.utc):
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

        return TokenResponseDTO(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    async def forgot_password(self, data: ForgotPasswordDTO) -> None:
        user = await self.user_repo.get_by_email(data.email)

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


    async def reset_password(self, data: ResetPasswordDTO) -> None:

        reset = await self.reset_repo.get_valid(data.token)

        if not reset:
            raise TokenInvalid("Invalid reset token")

        if reset.expires_at < datetime.now(timezone.utc):
            raise TokenExpired("Reset token expired")

        user = await self.user_repo.get_by_id(int(reset.user_id))

        if not user:
            raise TokenInvalid("Invalid reset token")

        user.hashed_password = hash_password(data.new_password)
        await self.user_repo.save_user(user)

        await self.reset_repo.invalidate(data.token)
        await self.refresh_repo.revoke_all_for_user(int(reset.user_id))


    async def change_password(self, current_user: User, data: ChangePasswordDTO) -> None:
        if not verify_password(data.old_password, current_user.hashed_password):
            raise InvalidCredentials("Invalid password")

        current_user.hashed_password = hash_password(data.new_password)
        await self.user_repo.save_user(current_user)

        await self.refresh_repo.revoke_all_for_user(int(current_user.id))
from datetime import datetime, timedelta, timezone

from app.core.security.passwords import (
    verify_password,
    hash_password,)

from app.core.security.tokens import (create_access_token,
                                      create_refresh_token,
                                      )

from app.shared.exceptions import (
    InvalidCredentials,
    TokenInvalid,
    TokenExpired,
)

from app.auth.repositories.refresh_token import RefreshTokenRepository
from app.users.repository import UserRepository

from app.database.uow import UnitOfWork
from app.core.config import settings


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        refresh_repo: RefreshTokenRepository,
        uow: UnitOfWork,
    ):
        self.user_repo = user_repo
        self.refresh_repo = refresh_repo
        self.uow = uow

    def login(self, email: str, password: str) -> dict:
        user = self.user_repo.get_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentials()

        try:
            self.refresh_repo.revoke_all_for_user(user.id)

            access_token = create_access_token(user.id)
            refresh_token = create_refresh_token(user.id)

            expires_at = datetime.now(timezone.utc) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

            self.refresh_repo.create(
                user_id=user.id,
                token=refresh_token,
                expires_at=expires_at,
            )

            self.uow.commit()

        except Exception:
            self.uow.rollback()
            raise

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    def logout(self, refresh_token: str) -> None:
        try:
            token = self.refresh_repo.get_by_token(refresh_token)

            if not token or token.is_revoked:
                raise TokenInvalid()

            self.refresh_repo.revoke(token)
            self.uow.commit()

        except Exception:
            self.uow.rollback()
            raise

    def refresh_token(self, refresh_token: str) -> dict:
        token = self.refresh_repo.get_by_token(refresh_token)

        if not token or token.is_revoked:
            raise TokenInvalid()

        if token.expires_at < datetime.now(timezone.utc):
            raise TokenExpired()

        try:
            access_token = create_access_token(token.user_id)
            new_refresh_token = create_refresh_token(token.user_id)

            self.refresh_repo.revoke(token)

            expires_at = datetime.now(timezone.utc) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

            self.refresh_repo.create(
                user_id=token.user_id,
                token=new_refresh_token,
                expires_at=expires_at,
            )

            self.uow.commit()

        except Exception:
            self.uow.rollback()
            raise

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
    ) -> None:
        user = self.user_repo.get_by_id(user_id)

        if not user or not verify_password(
            current_password, user.hashed_password
        ):
            raise InvalidCredentials()

        try:
            user.hashed_password = hash_password(new_password)
            self.refresh_repo.revoke_all_for_user(user.id)
            self.uow.commit()

        except Exception:
            self.uow.rollback()
            raise

    def forgot_password(self, email: str) -> None:
        """
        It doesn't reveal whether the user exists.
        The router handles sending the email.
        """
        user = self.user_repo.get_by_email(email)
        if not user:
            return

        try:
            token = create_refresh_token(user.id)
            expires_at = datetime.now(timezone.utc) + timedelta(
                hours=settings.PASSWORD_RESET_EXPIRE_HOURS
            )

            self.refresh_repo.create(
                user_id=user.id,
                token=token,
                expires_at=expires_at,
            )

            self.uow.commit()

        except Exception:
            self.uow.rollback()
            raise

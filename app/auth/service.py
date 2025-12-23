from datetime import datetime, timedelta, timezone

from app.auth.repositories.refresh_token import RefreshTokenRepository
from app.config import settings
from app.database.uow import UnitOfWork
from app.shared.exceptions import InvalidCredentials
from app.shared.security.passwords import verify_password
from app.shared.security.tokens import create_access_token, create_refresh_token
from app.users.repository import UserRepository


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
    
    """
    logout()
    refresh_token()
    change_password()
    forgot_password()
    reset_password()
    """
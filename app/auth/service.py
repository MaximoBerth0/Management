from datetime import datetime, timezone, timedelta
from app.auth.repositories.refresh_token_repo import RefreshTokenRepository
from app.users.repository import UserRepository
from app.auth.security import create_access_token, create_refresh_token, verify_password 
from app.shared.exceptions import InvalidCredentials
from app.config import settings

class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        refresh_repo: RefreshTokenRepository,
        db,
    ):
        self.user_repo = user_repo
        self.refresh_repo = refresh_repo
        self.db = db

    def login(self, email: str, password: str) -> dict:
        user = self.user_repo.get_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentials("Invalid credentials")

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

        self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.repositories.password_reset import PasswordResetTokenRepository
from app.auth.repositories.refresh_token import RefreshTokenRepository
from app.auth.service import AuthService
from app.core.security.tokens import verify_access_token
from app.database.session import get_session
from app.mail.mailer import Mailer
from app.shared.exceptions.auth_errors import TokenExpired, TokenInvalid
from app.users.models import User
from app.users.repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session),
) -> User:
    try:
        payload = verify_access_token(token)
    except (TokenInvalid, TokenExpired):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(int(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def get_auth_service(db = Depends(get_session)) -> AuthService:
    user_repo = UserRepository(db)
    refresh_repo = RefreshTokenRepository(db)
    reset_repo = PasswordResetTokenRepository(db)
    mailer = Mailer()

    return AuthService(
        user_repo=user_repo,
        refresh_repo=refresh_repo,
        reset_repo=reset_repo,
        mailer=mailer,
    )

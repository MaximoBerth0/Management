from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth.repositories.password_reset import PasswordResetTokenRepository
from app.auth.repositories.refresh_token import RefreshTokenRepository
from app.auth.service import AuthService
from app.database import get_db
from app.database.uow import UnitOfWork
from app.users.repository import UserRepository


def get_auth_service(
    db: Session = Depends(get_db),
) -> AuthService:
    uow = UnitOfWork(db)

    return AuthService(
        refresh_token_repo=RefreshTokenRepository(db),
        password_reset_repo=PasswordResetTokenRepository(db),
        user_repo=UserRepository(db),
        uow=uow,
    )

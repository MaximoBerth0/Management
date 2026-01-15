from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth.repositories.password_reset import PasswordResetTokenRepository
from app.auth.repositories.refresh_token import RefreshTokenRepository
from app.auth.service import AuthService
from app.database.session import get_db
from app.database.uow import UnitOfWork
from app.users.repository import UserRepository


def get_auth_service(
    db: Session = Depends(get_db),
) -> AuthService:
    uow = UnitOfWork(db)

    return AuthService(
        user_repo=UserRepository(db),
        refresh_token_repo=RefreshTokenRepository(db),
        password_reset_repo=PasswordResetTokenRepository(db),
        uow=uow,
    )

class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        refresh_token_repo: RefreshTokenRepository,
        password_reset_repo: PasswordResetTokenRepository,
        uow: UnitOfWork,
    ):
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo
        self.password_reset_repo = password_reset_repo
        self.uow = uow

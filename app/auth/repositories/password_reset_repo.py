from datetime import datetime
from typing import Optional

from app.auth.models import PasswordResetToken
from sqlalchemy import select, update
from sqlalchemy.orm import Session


class PasswordResetTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        token: str,
        expires_at: datetime,
    ) -> None:
        self.db.add(
            PasswordResetToken(
                user_id=user_id,
                token=token,
                expires_at=expires_at,
                used=False,
            )
        )

    def get_valid(self, token: str) -> Optional[PasswordResetToken]:
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token == token,
            PasswordResetToken.used.is_(False),
        )
        return self.db.scalar(stmt)

    def invalidate(self, token: str) -> None:
        stmt = (
            update(PasswordResetToken)
            .where(PasswordResetToken.token == token)
            .values(used=True)
        )
        self.db.execute(stmt)

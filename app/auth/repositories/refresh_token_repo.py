from datetime import datetime
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.auth.models import RefreshToken

class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        token: str,
        expires_at: datetime,
    ) -> None:
        self.db.add(
            RefreshToken(
                user_id=user_id,
                token=token,
                expires_at=expires_at,
                revoked=False,
            )
        )

    def get_active(self, token: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.revoked.is_(False),
        )
        return self.db.scalar(stmt)

    def revoke(self, token: str) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.token == token)
            .values(revoked=True)
        )
        self.db.execute(stmt)

    def revoke_all_for_user(self, user_id: int) -> None:
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked.is_(False),
            )
            .values(revoked=True)
        )
        self.db.execute(stmt)

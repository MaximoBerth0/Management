from datetime import datetime
from typing import Optional

from app.auth.models import RefreshToken
from sqlalchemy import select, update
from sqlalchemy.orm import Session


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
                token_hash=token,
                expires_at=expires_at,
                is_revoked=False,
            )
        )

    def get_by_token(self, token: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token)
        return self.db.scalar(stmt)

    def get_active(self, token: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token,
            RefreshToken.is_revoked.is_(False)

        )
        return self.db.scalar(stmt)

    def revoke(self, token: RefreshToken) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.id == token.id)
            .values(is_revoked=True)
        )
        self.db.execute(stmt)

    def revoke_all_for_user(self, user_id: int) -> None:
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked.is_(False)

            )
            .values(revoked=True)
        )
        self.db.execute(stmt)

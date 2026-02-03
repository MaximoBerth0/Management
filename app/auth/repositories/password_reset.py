from datetime import datetime
from typing import Optional

from app.auth.models import PasswordResetToken
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class PasswordResetTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
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
        await self.db.commit()

    async def get_valid(self, token: str) -> Optional[PasswordResetToken]:
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token == token,
            PasswordResetToken.used.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def invalidate(self, token: str) -> None:
        stmt = (
            update(PasswordResetToken)
            .where(PasswordResetToken.token == token)
            .values(used=True)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def invalidate_all_for_user(self, user_id: int) -> None:
        stmt = (
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.used.is_(False),
            )
            .values(used=True)
        )
        await self.db.execute(stmt)
        await self.db.commit()

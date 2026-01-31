from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
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
        await self.db.commit()

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active(self, token: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token,
            RefreshToken.is_revoked.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke(self, token_id: int) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.id == token_id)
            .values(is_revoked=True)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def revoke_all_for_user(self, user_id: int) -> None:
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked.is_(False),
            )
            .values(is_revoked=True)
        )
        await self.db.execute(stmt)
        await self.db.commit()

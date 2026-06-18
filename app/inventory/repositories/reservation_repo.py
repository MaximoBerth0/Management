import uuid

from app.inventory.models.reservation import StockReservation
from sqlalchemy.ext.asyncio import AsyncSession


class ReservationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_reservation(
        self, order_item_id: uuid.UUID, stock_id: uuid.UUID, quantity: int
    ) -> StockReservation:
        reservation = StockReservation.create(
            order_item_id=order_item_id,
            stock_id=stock_id,
            quantity=quantity,
        )
        self.db.add(reservation)
        await self.db.flush()
        return reservation

from app.inventory.models.enums import ReservationStatus
from app.inventory.models.reservation import StockReservation
from app.inventory.models.stock import InventoryStock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

"""
# used by order service, atomic operations 

async def reserve_stock()         
async def release_reservation()   
async def fulfill_reservation()  
"""

class ReservationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def reserve_stock(
        self,
        stock_id: int,
        order_item_id: int,
        quantity: int
    ) -> StockReservation:
        stmt = (
            select(InventoryStock)
            .where(InventoryStock.id == stock_id)
            .with_for_update()  
        )
        result = await self.db.execute(stmt)
        stock = result.scalar_one_or_none()

        if not stock:
            raise ValueError("Stock not found")

        available = stock.quantity - stock.reserved_quantity
        if available < quantity:
            raise ValueError(f"Insufficient stock. Available: {available}")

        stock.reserved_quantity += quantity

        reservation = StockReservation.create(
            order_item_id=order_item_id,
            stock_id=stock_id,
            quantity=quantity,
        )
        self.db.add(reservation)

        return reservation
    
    async def release_reservation(self, reservation_id:int) -> StockReservation:
        reservation = await self.db.get(StockReservation, reservation_id)
        if not reservation:
            raise ValueError("Reservation not found")

        stmt = (
            select(InventoryStock)
            .where(InventoryStock.id == reservation.stock_id)
            .with_for_update()
        )
        result = await self.db.execute(stmt)
        stock = result.scalar_one_or_none()
        if not stock:
            raise ValueError("Stock not found")

        stock.quantity += reservation.quantity
        stock.reserved_quantity += reservation.quantity

        reservation.status = ReservationStatus.RELEASED

        return reservation

    async def fulfill_reservation(self, reservation_id: int) -> StockReservation:
        reservation = await self.db.get(StockReservation, reservation_id)
        if not reservation:
            raise ValueError("Reservation not found")

        stmt = (
            select(InventoryStock)
            .where(InventoryStock.id == reservation.stock_id)
            .with_for_update()
        )
        result = await self.db.execute(stmt)
        stock = result.scalar_one_or_none()
        if not stock:
            raise ValueError("Stock not found")

        stock.quantity -= reservation.quantity
        stock.reserved_quantity -= reservation.quantity

        reservation.status = ReservationStatus.FULFILLED

        return reservation
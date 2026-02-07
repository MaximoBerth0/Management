from typing import Optional

from app.inventory.models.enums import StockReservationStatus
from app.inventory.models.inventory_model import (
    InventoryStock,
    StockMovement,
    StockReservation,
)
from app.shared.exceptions.inventory_errors import ReservationNotExists, StockNotFound
from sqlalchemy import func, select
from sqlalchemy.engine import ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession

"""
functions are pure persistence + locking (without business logic): 

get_by_product_id
create_inventory
get_product_total_stock
get_for_update
save
add_movement
add_reservation
get_reserved_amount
get_reservation_for_update
list_reservations
"""

class StockInventoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Inventory

    async def get_by_product_id(
        self,
        product_id: int,
    ) -> Optional[InventoryStock]:
        stmt = (
            select(InventoryStock)
            .where(InventoryStock.product_id == product_id)
        )

        result: ScalarResult[InventoryStock] = await self.db.scalars(stmt)
        return result.first()

    async def create_inventory(
        self,
        inventory: InventoryStock,
    ) -> InventoryStock:
        self.db.add(inventory)
        await self.db.flush()
        return inventory

    async def get_product_total_stock(
        self,
        product_id: int,
    ) -> int:
        stmt = (
            select(func.coalesce(func.sum(InventoryStock.quantity_available), 0))
            .where(InventoryStock.product_id == product_id)
        )

        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_for_update(
        self,
        *,
        product_id: int,
        location_id: int,
    ) -> InventoryStock:
        stmt = (
            select(InventoryStock)
            .where(
                InventoryStock.product_id == product_id,
                InventoryStock.location_id == location_id,
            )
            .with_for_update()
        )

        result = await self.db.execute(stmt)
        stock = result.scalar_one_or_none()

        if stock is None:
            raise StockNotFound(
                f"Stock not found for product={product_id}, location={location_id}"
            )

        return stock

    async def save(self, stock: InventoryStock) -> None:
        self.db.add(stock)

    # Movements

    async def add_movement(
        self,
        movement: StockMovement,
    ) -> None:
        self.db.add(movement)

    # Reservations

    async def add_reservation(
        self,
        reservation: StockReservation,
    ) -> None:
        self.db.add(reservation)

    async def get_reserved_amount(
        self,
        product_id: int,
    ) -> int:
        stmt = (
            select(InventoryStock.quantity_reserved)
            .where(InventoryStock.product_id == product_id)
        )

        result = await self.db.execute(stmt)
        reserved = result.scalar_one_or_none()

        if reserved is None:
            raise StockNotFound(
                f"Stock not found for product={product_id}"
            )

        return reserved

    async def get_reservation_for_update(
            self,
            *,
            reservation_id: int,
    ) -> StockReservation:
        stmt = (
            select(StockReservation)
            .where(StockReservation.id == reservation_id)
            .with_for_update()
        )

        result = await self.db.execute(stmt)
        reservation = result.scalar_one_or_none()

        if reservation is None:
            raise ReservationNotExists(
                f"Reservation not found: id={reservation_id}"
            )

        return reservation

    async def list_reservations(
        self,
        *,
        product_id: Optional[int] = None,
        user_id: Optional[int] = None,
        active_only: bool = True,
    ) -> list[StockReservation]:
        stmt = select(StockReservation)

        if product_id is not None:
            stmt = stmt.where(StockReservation.product_id == product_id)

        if user_id is not None:
            stmt = stmt.where(StockReservation.user_id == user_id)

        if active_only:
            stmt = stmt.where(
                StockReservation.status == StockReservationStatus.ACTIVE
            )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
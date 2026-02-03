from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy import select, update, func
from sqlalchemy.engine import ScalarResult

from app.inventory.models import (
    InventoryStock,
    StockReservation, StockReservationStatus, StockMovement, StockMovementType,
)
from app.shared.exceptions.inventory_errors import InventoryDBError, InsufficientStock, StockNotFound, ReservationInactive, ReservationNotExists



class StockInventoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_product_id(
            self,
            product_id: int
    ) -> Optional[InventoryStock]:

        stmt = (
            select(InventoryStock)
            .where(InventoryStock.product_id == product_id)
        )

        result: ScalarResult[InventoryStock] = await self.db.scalars(stmt)
        return result.first()

    async def create_inventory(
        self,
        inventory: InventoryStock
    ) -> InventoryStock:
        self.db.add(inventory)
        await self.db.flush()
        return inventory

    async def increase_available_stock(
            self,
            *,
            product_id: int,
            location_id: int,
            amount: int
    ) -> None:
        stmt = (
            update(InventoryStock)
            .where(
                InventoryStock.product_id == product_id,
                InventoryStock.location_id == location_id,
            )
            .values(
                quantity_available=InventoryStock.quantity_available + amount
            )
        )

        result = await self.db.execute(stmt)

        if result.rowcount == 0:   # type: ignore[attr-defined]
            raise InventoryDBError(
                f"Stock not found for product={product_id} location={location_id}"
            )

    async def decrease(
            self,
            *,
            product_id: int,
            location_id: int,
            amount: int
    ) -> None:
        stmt = (
            update(InventoryStock)
            .where(
                InventoryStock.product_id == product_id,
                InventoryStock.location_id == location_id,
                InventoryStock.quantity_available >= amount,
            )
            .values(
                quantity_available=InventoryStock.quantity_available - amount
            )
        )

        result = await self.db.execute(stmt)

        if result.rowcount == 0: # type: ignore[attr-defined]
            raise InventoryDBError(
                f"Stock not found or insufficient stock "
                f"for product={product_id} location={location_id}"
            )

    async def get_product_total_stock(
            self,
            product_id: int
    ) -> int:
        stmt = (
            select(func.coalesce(func.sum(InventoryStock.quantity_available), 0))
            .where(InventoryStock.product_id == product_id)
        )

        result = await self.db.execute(stmt)
        return result.scalar_one()

    # Reservations
    async def reserve(
            self,
            *,
            product_id: int,
            amount: int,
            user_id: int | None = None,
            reason: str | None = None,
    ) -> StockReservation:
        stmt = (
            select(InventoryStock)
            .where(InventoryStock.product_id == product_id)
            .with_for_update()
        )

        result = await self.db.execute(stmt)
        stock = result.scalar_one_or_none()

        if stock is None:
            raise StockNotFound("Stock not found for product")

        if stock.quantity_available < amount:
            raise InsufficientStock(
                f"Available={stock.quantity_available}, requested={amount}"
            )

        stock.quantity_available -= amount
        stock.quantity_reserved += amount

        reservation = StockReservation(
            product_id=product_id,
            amount=amount,
            user_id=user_id,
            status=StockReservationStatus.ACTIVE,
        )
        self.db.add(reservation)

        movement = StockMovement(
            stock=stock,
            type=StockMovementType.RESERVE,
            quantity=amount,
            reason=reason,
            created_by_user_id=user_id,
        )
        self.db.add(movement)

        await self.db.flush()

        return reservation



    async def release_reservation(
        self,
        reservation_id: int
    ) -> None:
        stmt = (
            select(StockReservation)
            .where(StockReservation.id == reservation_id)
            .with_for_update()
        )

        result = await self.db.execute(stmt)
        reservation = result.scalar_one_or_none()

        if reservation is None:
            raise ReservationNotExists("Reservation not found")

        if reservation.status != StockReservationStatus.ACTIVE:
            raise ReservationInactive("Reservation is not active")

        stmt = (
            select(InventoryStock)
            .where(InventoryStock.product_id == reservation.product_id)
            .with_for_update()
        )

        result = await self.db.execute(stmt)
        stock = result.scalar_one_or_none()

        stock.quantity_reserved -= reservation.amount
        stock.quantity_available += reservation.amount

        reservation.status = StockReservationStatus.RELEASED

        movement = StockMovement(
            stock=stock,
            type=StockMovementType.RELEASE,
            quantity=reservation.amount,
            reason="Reservation released",
            created_by_user_id=reservation.user_id,
        )

        self.db.add(movement)

        await self.db.flush()


        await self.db.flush()

    async def confirm_reservation(
            self,
            reservation_id: int
    ) -> None:
        stmt = (
            select(StockReservation)
            .where(StockReservation.id == reservation_id)
            .with_for_update()
        )

        result = await self.db.execute(stmt)
        reservation = result.scalar_one_or_none()

        if reservation is None:
            raise ReservationNotExists("Reservation not found")

        if reservation.status != StockReservationStatus.ACTIVE:
            raise ReservationInactive("Reservation is not active")

        stmt = (
            select(InventoryStock)
            .where(InventoryStock.product_id == reservation.product_id)
            .with_for_update()
        )

        result = await self.db.execute(stmt)
        stock = result.scalar_one_or_none()

        if stock is None:
            raise StockNotFound("Stock not found for product")

        stock.quantity_reserved -= reservation.amount

        movement = StockMovement(
            stock=stock,
            type=StockMovementType.OUT,
            quantity=reservation.amount,
            reason="Reservation confirmed",
            created_by_user_id=reservation.user_id,
        )
        self.db.add(movement)

        reservation.status = StockReservationStatus.CONFIRMED

        await self.db.flush()

    async def get_reserved_amount(
            self,
            product_id: int
    ) -> int:
        stmt = (
            select(InventoryStock.quantity_reserved)
            .where(InventoryStock.product_id == product_id)
        )

        result = await self.db.execute(stmt)
        reserved = result.scalar_one_or_none()

        if reserved is None:
            raise StockNotFound("Stock not found for product")

        return reserved

    async def list_reservations(
            self,
            *,
            product_id: Optional[int] = None,
            user_id: Optional[int] = None,
            active_only: bool = True
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





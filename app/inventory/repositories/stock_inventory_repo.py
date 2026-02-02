from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.engine import ScalarResult

from app.inventory.models import (
    InventoryStock,
    StockReservation,
)


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

        if result.rowcount == 0:
            raise InventoryNotFound(
                f"Stock not found for product={product_id} location={location_id}"
            )

    async def decrease(
        self,
        *,
        product_id: int,
        amount: int
    ) -> None:
        """
        Decrementa el stock total
        (no valida negativos, eso es del service)
        """
        ...

    async def get_total_quantity(
        self,
        product_id: int
    ) -> int:
        """
        Cantidad total en inventario
        """
        ...

    # Reservations
    async def reserve(
        self,
        *,
        product_id: int,
        amount: int,
        reserved_for: str,
        employee_id: int
    ) -> StockReservation:
        """
        Crea una reserva de stock a nombre de alguien ("X")
        """
        ...

    async def release_reservation(
        self,
        reservation_id: int
    ) -> None:
        """
        Libera una reserva activa
        """
        ...

    async def confirm_reservation(
        self,
        reservation_id: int
    ) -> None:
        """
        Confirma una reserva (se convierte en salida real)
        """
        ...

    async def get_reserved_amount(
        self,
        product_id: int
    ) -> int:
        """
        Cantidad total reservada de un producto
        """
        ...

    async def list_reservations(
        self,
        *,
        product_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        active_only: bool = True
    ) -> List[StockReservation]:
        """
        Lista reservas con filtros
        """
        ...




from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from typing import Optional, List
from app.inventory.models import

from app.inventory.models import (
    StockInventory,
    StockReservation,
)


class StockInventoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ======================================================
    # Inventory (estado del stock)
    # ======================================================

    async def get_by_product_id(
        self,
        product_id: int
    ) -> Optional[StockInventory]:
        """
        Devuelve el estado de stock de un producto
        """
        ...

    async def create_inventory(
        self,
        inventory: StockInventory
    ) -> StockInventory:
        """
        Crea el registro de inventario para un producto
        """
        ...

    async def increase(
        self,
        *,
        product_id: int,
        amount: int
    ) -> None:
        """
        Incrementa el stock total
        """
        ...

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

    # ======================================================
    # Reservations
    # ======================================================

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




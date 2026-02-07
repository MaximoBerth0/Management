from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.unit_of_work import UnitOfWork
from app.database.session import get_session
from app.inventory.repositories.product_repo import ProductRepository
from app.inventory.repositories.stock_inventory_repo import StockInventoryRepository
from app.inventory.service import InventoryService


def provide_inventory_service(
    db: AsyncSession = Depends(get_session),
) -> InventoryService:
    uow = UnitOfWork()

    return InventoryService(
        product_repo=ProductRepository(db),
        stock_inventory_repo=StockInventoryRepository(db),
        uow=uow,
    )

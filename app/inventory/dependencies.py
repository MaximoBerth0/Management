from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.inventory.repositories.category_repo import CategoryRepository
from app.inventory.repositories.location_repo import LocationRepository
from app.inventory.repositories.product_repo import ProductRepository
from app.inventory.repositories.reservation_repo import ReservationRepository
from app.inventory.repositories.stock_repo import StockRepository
from app.inventory.service import InventoryService


def provide_inventory_service(
    db: AsyncSession = Depends(get_session),
) -> InventoryService:
    return InventoryService(
        stock_repo=StockRepository(db),
        product_repo=ProductRepository(db),
        category_repo=CategoryRepository(db),
        location_repo=LocationRepository(db),
        reservation_repo=ReservationRepository(db),
    )

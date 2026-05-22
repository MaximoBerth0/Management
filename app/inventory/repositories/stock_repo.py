from app.inventory.models.stock import InventoryStock, StockMovement
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class StockRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, stock_id: int) -> InventoryStock | None:
        stmt = select(InventoryStock).where(InventoryStock.id == stock_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_movement(self, movement: StockMovement) -> StockMovement:
        self.db.add(movement)
        await self.db.commit()
        await self.db.refresh(movement)
        return movement
    
    async def list_movements_by_stock(self, stock_id: int) -> list[StockMovement]:
        stmt = (
            select(StockMovement)
            .where(StockMovement.stock_id == stock_id)
            .order_by(StockMovement.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    

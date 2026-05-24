from app.inventory.models.stock import InventoryStock, StockMovement
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class StockRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

# inventory 
    async def get_stock(self, stock_id: int) -> InventoryStock | None:
        stmt = select(InventoryStock).where(InventoryStock.id == stock_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def initialize_stock(self, location_id: int, product_id: int, quantity: int, reorder_point: int) -> InventoryStock:
        stock = InventoryStock(
            location_id=location_id,
            product_id=product_id,
            quantity=quantity,
            reorder_point=reorder_point,
        )
        self.db.add(stock)
        await self.db.commit()
        await self.db.refresh(stock)
        return stock


    async def add_stock()
    async def remove_stock()
    async def adjust_stock()        # new quantity 
    async def get_available_stock() # stock.quantity - stock.reserved_quantity
    async def list_stock_movements()       
    async def get_stock_by_location() 


# used by orders/ 
    async def reserve_stock()          
    async def release_reservation()    
    async def fulfill_reservation() 
    

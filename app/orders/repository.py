from sqlalchemy.ext.asyncio import AsyncSession
from app.orders.models.order import Order

class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

# Order 

    async def create_order(self, user_id: int) -> Order:
        order = Order.create(user_id=user_id)
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order

  # OrderItem 

    def append_item(self)
        
    def remove_item(self)
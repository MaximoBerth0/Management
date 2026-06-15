from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.orders.models.order import Order, OrderItem


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Order

    async def get_order(self, order_id: int) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items).selectinload(OrderItem.reservation))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_order(self, user_id: int) -> Order:
        order = Order.create(user_id=user_id)
        self.db.add(order)
        await self.db.commit()
        return await self.get_order(order.id)

    # OrderItem

    async def append_item(
        self, order_id: int, product_id: int, quantity: int
    ) -> Order | None:
        order = await self.get_order(order_id)
        if order is None:
            return None

        item = order.add_item(product_id=product_id, quantity=quantity)
        self.db.add(item)
        await self.db.commit()
        return await self.get_order(order_id)

    async def remove_item(self, order_id: int, product_id: int) -> Order | None:
        order = await self.get_order(order_id)
        if order is None:
            return None

        await self.db.refresh(order, attribute_names=["items"])
        order.remove_item(product_id)
        await self.db.commit()
        return order

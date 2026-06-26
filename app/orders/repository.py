import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.orders.exceptions import OrderCodeGenerationError
from app.orders.models.order import Order, OrderItem

_MAX_CODE_RETRIES = 5

class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Order

    async def get_order(self, order_id: uuid.UUID) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items).selectinload(OrderItem.reservation))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_order_by_code(self, code: str) -> Order | None:
        stmt = (
            select(Order)
            .where(Order.code == code)
            .options(selectinload(Order.items).selectinload(OrderItem.reservation))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_orders_by_user(self, user_id: uuid.UUID) -> Sequence[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items).selectinload(OrderItem.reservation))
            .order_by(Order.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_order(self, user_id: uuid.UUID) -> Order:
        for _ in range(_MAX_CODE_RETRIES):
            order = Order.create(user_id=user_id)  # generate a new code 
            self.db.add(order)
            try:
                await self.db.commit()
            except IntegrityError:
                await self.db.rollback()
                continue  # rarely collision
            return await self.get_order(order.id)

        raise OrderCodeGenerationError()

    # OrderItem

    async def append_item(
        self, order_id: uuid.UUID, product_id: uuid.UUID, quantity: int
    ) -> Order | None:
        order = await self.get_order(order_id)
        if order is None:
            return None

        item = order.add_item(product_id=product_id, quantity=quantity)
        self.db.add(item)
        await self.db.commit()
        return await self.get_order(order_id)

    async def remove_item(self, order_id: uuid.UUID, product_id: uuid.UUID) -> Order | None:
        order = await self.get_order(order_id)
        if order is None:
            return None

        await self.db.refresh(order, attribute_names=["items"])
        order.remove_item(product_id)
        await self.db.commit()
        return order

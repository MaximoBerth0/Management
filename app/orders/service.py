from app.database.unit_of_work import UnitOfWork
from app.orders.models.orders_model import Order
from app.orders.repository import OrderRepository
from app.inventory.repositories.product_repo import ProductRepository
from app.shared.exceptions.order_errors import OrderNotFoundError
from app.orders.models.enums import OrderStatus

"""
    async def create_order(...)
    async def cancel_order(...)
    async def confirm_order(...)
    async def add_item(...) only in OrderStatus = created
    async def remove_item(...)
    async def get_order(order_id...)
    async def list_orders(...)
"""

class OrderService:
    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    async def create_order(self, user_id: int) -> Order:
        async with self.unit_of_work as session:
            repo = OrderRepository(session)

            order = Order.create(user_id)

            await repo.create(order)

            return order

    async def cancel_order(self, order_id: int):
        async with self.unit_of_work as session:
            repo = OrderRepository(session)

            order = await repo.get_by_id(order_id)

            if not order:
                raise ValueError("Order not found")

            order.cancel()

    async def confirm_order(self, order_id: int):
        async with self.unit_of_work as session:
            repo = OrderRepository(session)
            order = await repo.get_by_id(order_id)

            if not order:
                raise ValueError("Order not found")

            order.confirm()

    async def add_item(
            self,
            order_id: int,
            product_id: int,
            quantity: int,
    ):

        async with self.unit_of_work as session:
            repo = OrderRepository(session)

            order = await repo.get_by_id(order_id)

            if not order:
                raise ValueError("Order not found")

            order.add_item(product_id, quantity)

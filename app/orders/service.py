from app.core.unit_of_work import UnitOfWork
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


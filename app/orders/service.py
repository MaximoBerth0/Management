from app.orders.models.order import Order
from app.orders.models.enums import OrderStatus
from app.orders.repository import OrderRepository
"""
create_order()
add_item_to_order()
remove_item_from_order() 
confirm_order()
cancel_order()
complete_order()

"""

class OrderService:
    def __init__(self, order_repo: OrderRepository):
        self.order_repo = order_repo

    async def create_order(self, user_id: int) -> Order:
        return await self.order_repo.create_order(user_id)

    async def add_item_to_order(self, order_id: int, product_id: int, quantity: int):

    async def remove_item_from_order(self, order_id: int, product_id: int, quantity: int):


    
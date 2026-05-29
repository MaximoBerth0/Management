from sqlalchemy.ext.asyncio import AsyncSession

from app.inventory.service import InventoryService
from app.orders.models.enums import OrderStatus
from app.orders.models.order import Order
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
    def __init__(
        self,
        db: AsyncSession,
        order_repo: OrderRepository,
        inventory_service: InventoryService,
    ):
        self.db = db
        self.order_repo = order_repo
        self.inventory_service = inventory_service

    async def create_order(self, user_id: int) -> Order:
        return await self.order_repo.create_order(user_id)

    async def add_item_to_order(self, order_id: int, product_id: int, quantity: int) -> Order:
        order = await self.order_repo.append_item(order_id, product_id, quantity)
        if order is None:
            raise ValueError("Order not found")
        return order


    async def remove_item_from_order(self, order_id: int, product_id: int) -> Order:
        order = await self.order_repo.remove_item(order_id, product_id)
        if order is None:
            raise ValueError("Order not found")
        return order
    
    async def confirm_order(self, order_id: int, location_id: int, user_id: int) -> Order:
        async with self.db.begin(): 
            
            order = await self.order_repo.get_order(order_id)
            if order is None:
                raise ValueError("Order not found")
            if order.status != OrderStatus.CREATED:
                raise ValueError(f"Order is not pending, current status: {order.status}")
            
            for item in order.items:
                await self.inventory_service.reserve_for_item(
                    order_item_id=item.id,
                    product_id=item.product_id,
                    location_id=location_id,
                    quantity=item.quantity,
                )

            order.status = OrderStatus.CONFIRMED

        return order

    async def cancel_order(self, order_id: int) -> Order:
        async with self.db.begin():
            order = await self.order_repo.get_order(order_id)
            if order is None:
                raise ValueError("Order not found")
            
            if order.status == OrderStatus.CONFIRMED:
                for item in order.items:
                    if item.reservation is not None:
                        await self.inventory_service.release_reservation(item.reservation.id)
            
            order.cancel()
            return order
    
    async def complete_order(self, order_id: int) -> Order:
        async with self.db.begin():
            order = await self.order_repo.get_order(order_id)
            if order is None:
                raise ValueError("Order not found")
            
            for item in order.items:
                if item.reservation is not None:
                    await self.inventory_service.fulfill_reservation(item.reservation.id)
            
            order.complete()
            return order
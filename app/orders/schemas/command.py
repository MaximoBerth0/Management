from datetime import datetime
from typing import List

from app.orders.models.enums import OrderStatus
from app.orders.models.orders_model import OrderItem
from pydantic import BaseModel

# input

class CreateOrderCommand(BaseModel):
    items: List[OrderItem]


class CreateOrderItemCommand(BaseModel):
    product_id: int
    quantity: int

# output

class OrderItemDTO(BaseModel):
    product_id: int
    quantity: int
    unit_price: int


class OrderDTO(BaseModel):
    id: int
    status: List[OrderStatus]
    total_amount: int
    created_at: datetime
    items: List[OrderItemDTO]



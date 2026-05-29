from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.orders.models.enums import OrderStatus


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# request


class AddItemRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class ConfirmOrderRequest(BaseModel):
    location_id: int = Field(..., gt=0)


# response


class OrderItemResponse(ORMModel):
    id: int
    product_id: int
    quantity: int
    created_at: datetime


class OrderResponse(ORMModel):
    id: int
    user_id: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []

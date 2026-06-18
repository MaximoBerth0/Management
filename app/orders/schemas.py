import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.orders.models.enums import OrderStatus


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# request


class AddItemRequest(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(..., gt=0)


# response


class OrderItemResponse(ORMModel):
    id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    created_at: datetime


class OrderResponse(ORMModel):
    id: uuid.UUID
    user_id: uuid.UUID
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []

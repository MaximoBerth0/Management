from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.inventory.models.enums import StockMovementType


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# request


class ProductCreate(ORMModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)
    category_id: int = Field(..., gt=0)


class ProductUpdate(ORMModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    sku: str | None = Field(None, min_length=1, max_length=100)


class CategoryCreate(ORMModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=255)


class AddProductToCategory(ORMModel):
    product_id: int


class RemoveProducFromCategory(ORMModel):
    product_id: int


class LocationCreate(ORMModel):
    name: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=255)
    address: str = Field(..., min_length=1, max_length=255)


class LocationUpdate(ORMModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    city: str | None = Field(None, min_length=1, max_length=255)
    address: str | None = Field(None, min_length=1, max_length=255)


class StockInitialize(ORMModel):
    product_id: int = Field()
    quantity: int = Field()
    reorder_point: int = Field()


class StockTransaction(ORMModel):
    product_id: int = Field()
    quantity: int = Field()
    reason: Optional[str] = Field(None, max_length=500)


# response


class ProductListItemResponse(ORMModel):
    id: int
    name: str
    sku: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductResponse(ORMModel):
    id: int
    name: str
    sku: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CategoryResponse(ORMModel):
    id: int
    name: str
    description: str


class StockMovementResponse(ORMModel):
    id: int
    stock_id: int
    movement_type: StockMovementType
    quantity: int
    previous_quantity: int
    new_quantity: int
    created_by: int
    created_at: datetime


class StockResponse(ORMModel):
    id: int
    location_id: int
    product_id: int
    quantity: int
    reorder_point: int
    created_at: datetime
    updated_at: datetime


class StockMovementListResponse(ORMModel):
    items: List[StockMovementResponse]
    total: int


class LocationResponse(ORMModel):
    id: int
    name: str
    city: str
    address: str


class LocationListResponse(ORMModel):
    items: List[LocationResponse]
    total: int


class StockListResponse(ORMModel):
    items: List[StockResponse]
    total: int

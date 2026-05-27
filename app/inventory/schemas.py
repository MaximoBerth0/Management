from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.inventory.models.enums import StockMovementType


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# request

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)
    category_id: int = Field(..., gt=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    sku: str | None = Field(None, min_length=1, max_length=100)

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=255)

class AddProductToCategory(BaseModel):
    product_id: int

class RemoveProducFromCategory(BaseModel):
    product_id: int

class StockInitialize(BaseModel):
    location_id: int = Field()
    product_id: int = Field()
    quantity: int = Field()
    reorder_point: int = Field()

class StockTransaction(BaseModel):
    product_id: int = Field()
    location_id: int = Field()
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

class StockMovementResponse(BaseModel):
    id: int
    stock_id: int
    movement_type: StockMovementType
    quantity: int
    previous_quantity: int
    new_quantity: int
    created_by: int
    created_at: datetime

class StockResponse(BaseModel):
    id: int
    location_id: int
    product_id: int
    quantity: int
    reorder_point: int
    created_at: datetime
    updated_at: datetime

class StockMovementListResponse(BaseModel):
    items: List[StockMovementResponse]  
    total: int

class StockListResponse(BaseModel):
    items: List[StockResponse]  
    total: int
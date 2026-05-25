# schema for router.py, only http for request and response
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# product request

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: str = Field(..., min_length=1, max_length=100)
    category_id: int = Field(..., gt=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    sku: str | None = Field(None, min_length=1, max_length=100)


# product response

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

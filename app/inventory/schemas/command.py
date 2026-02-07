from datetime import datetime

from app.inventory.models.enums import StockMovementType, StockReservationStatus
from pydantic import BaseModel, Field

# ==== inputs ====

class CreateProductCommand(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    sku: str = Field(min_length=1, max_length=100)


class UpdateProductCommand(BaseModel):
    product_id: int
    name: str | None = Field(default=None, min_length=1, max_length=255)
    sku: str | None = Field(default=None, min_length=1, max_length=100)


class CreateStockMovementCommand(BaseModel):
    product_id: int
    location_id: int
    quantity: int = Field(gt=0)
    type: StockMovementType
    reason: str | None = None


class CreateReservationCommand(BaseModel):
    product_id: int
    location_id: int
    quantity: int = Field(gt=0)
    user_id: int | None = None


class ConfirmReservationCommand(BaseModel):
    reservation_id: int


class ReleaseReservationCommand(BaseModel):
    reservation_id: int
    reason: str | None = None


# ==== outputs ====

class ProductDTO(BaseModel):
    id: int
    name: str
    sku: str
    is_active: bool


class ReservationDTO(BaseModel):
    id: int
    product_id: int
    location_id: int
    quantity: int
    status: StockReservationStatus
    user_id: int | None
    created_at: datetime


class StockMovementDTO(BaseModel):
    id: int
    product_id: int
    location_id: int
    type: StockMovementType
    quantity: int
    reason: str | None
    created_at: datetime




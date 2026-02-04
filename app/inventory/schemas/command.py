from pydantic import BaseModel, Field, field_validator
from app.inventory.models.enums import StockMovementType


class CreateProductCommand(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    sku: str = Field(min_length=1, max_length=100)


class DeactivateProductCommand(BaseModel):
    product_id: int
    reason: str | None = None


class ProductDTO(BaseModel):
    id: int
    name: str
    sku: str
    is_active: bool


class CreateStockMovementCommand(BaseModel):
    product_id: int
    location_id: int
    quantity: int = Field(gt=0)
    type: StockMovementType
    reason: str | None = None


class CreateReservationCommand(BaseModel):
    product_id: int
    location_id: int
    amount: int = Field(gt=0)
    user_id: int | None = None


class ConfirmReservationCommand(BaseModel):
    reservation_id: int


class ReleaseReservationCommand(BaseModel):
    reservation_id: int
    reason: str | None = None


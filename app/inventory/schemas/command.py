"""
product
- create product
- deactivate product
- see product

stock
- get stock level (by product & location)
- list stock levels for product
- increase stock
- decrease stock
- adjust stock (admin only)

reservation
- create reservation
- confirm reservation
- release reservation
- get reservation

"""

from pydantic import BaseModel, Field, field_validator


class CreateProductCommand(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    sku: str = Field(min_length=1, max_length=100)


class DeactivateProductCommand(BaseModel):
    product_id: int
    reason: str | None = None


class ProductDTO(BaseModel):
    id: int
    name: str
    description: str | None
    sku: str
    is_active: bool


class CreateReservationCommand(BaseModel):
    product_id: int
    location_id: int
    amount: int = Field(gt=0)
    user_id: int | None = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("amount must be greater than zero")
        return v

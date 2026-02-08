from pydantic import BaseModel, Field, model_validator


class CreateProductIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    sku: str = Field(min_length=3, max_length=50)


class UpdateProductIn(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    sku: str | None = Field(default=None, min_length=3, max_length=50)

    @model_validator(mode="after")
    def at_least_one_field_provided(self):
        if self.name is None and self.sku is None:
            raise ValueError("At least one field must be provided")
        return self


class StockInIn(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    location_id: int
    reason: str | None = None


class StockOutIn(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    location_id: int
    reason: str | None = None


class StockReserveIn(BaseModel):
    product_id: int = Field(..., gt=0)
    location_id: int
    quantity: int = Field(..., gt=0)
    reference_id: str = Field(
        ...,
        min_length=3,
    )

class StockReleaseIn(BaseModel):
    product_id: int = Field(..., gt=0)
    location_id: int
    quantity: int = Field(..., gt=0)
    reference_id: str = Field(
        ...,
        min_length=3)


class StockAdjustIn(BaseModel):
    product_id: int = Field(..., gt=0)
    location_id: int
    quantity: int
    reason: str = Field(
        ...,
        min_length=5)

class ReleaseReservationIn(BaseModel):
    reservation_id: int = Field(
        ...,
        gt=0,
    )
    reason: str | None = Field(
        default=None,
        min_length=3)


class ConfirmReservationIn(BaseModel):
    reservation_id: int = Field(..., gt=0)
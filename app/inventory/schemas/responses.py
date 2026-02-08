from app.inventory.models.enums import StockReservationStatus
from pydantic import BaseModel


class ProductOut(BaseModel):
    id: int
    name: str
    sku: str
    is_active: bool

    class Config:
        from_attributes = True


class StockOperationOut(BaseModel):
    product_id: int
    previous_quantity: int
    new_quantity: int


class StockReservationOut(StockOperationOut):
    reservation_id: int
    reservation_status: StockReservationStatus
    reserved_quantity: int
    user_id: int


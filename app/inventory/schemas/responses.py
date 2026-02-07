from pydantic import BaseModel


class ProductOut(BaseModel):
    id: int
    name: str
    sku: str
    is_active: bool

    class Config:
        from_attributes = True

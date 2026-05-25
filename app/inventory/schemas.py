# schema for router.py, only http for request and response
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# product response

class ProductListItemResponse(ORMModel):
    id: int
    name: str
    sku: str
    is_active: bool
    created_at: datetime

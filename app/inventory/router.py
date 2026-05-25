"""
GET    /inventory/products                             - list
GET    /inventory/products/{id}                        - get a product 
POST   /inventory/products                             - create product
PATCH  /inventory/products/{id}                        - update a product
DELETE /inventory/products/{id}                        - delete a product

POST   /inventory/categories                           - create category
DELETE /inventory/categories/{id}                      - delete category
POST   /inventory/categories/{category_id}/products    - add product to category
DELETE /inventory/categories/{category_id}/products    - remove product from category

POST   /inventory/stock/in                             - add stock
POST   /inventory/stock/out                            - remove stock  
POST   /inventory/stock/adjust                         - adjust stock
GET    /inventory/stock/movements                      - list stock movements
GET    /inventory/stock                                - get current stock levels

"""
from typing import List

from fastapi import APIRouter, Depends, status

from app.inventory.dependencies import provide_inventory_service
from app.inventory.models.enums import StockMovementType
from app.inventory.schemas import ProductListItemResponse
from app.inventory.service import InventoryService
from app.rbac.dependencies import require_permission
from app.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/inventory",
    tags=["INVENTORY"],
)

# products

@router.get(
    "/products",
    response_model=list[ProductListItemResponse],
    dependencies=[Depends(require_permission("inventory:view"))],
)
async def list_products(
    service: InventoryService = Depends(provide_inventory_service),
):
    return await service.list_products()







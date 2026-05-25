"""
GET    /inventory/products                             - list
GET    /inventory/products/{id}                        - get a product 
POST   /inventory/products                             - create product
PATCH  /inventory/products/{id}                        - update a product
DELETE /inventory/products/{id}                        - delete a product
POST   /inventory/products/{id}/activate               - activate a product


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
from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.inventory.dependencies import provide_inventory_service
from app.inventory.schemas import (
    ProductCreate,
    ProductListItemResponse,
    ProductResponse,
    ProductUpdate,
)
from app.inventory.service import InventoryService
from app.rbac.dependencies import require_permission

router = APIRouter(
    prefix="/inventory",
    tags=["INVENTORY"],
)

# products

@router.get(
    "/products",
    response_model=list[ProductListItemResponse],
    dependencies=[Depends(require_permission("product:view"))],
)
async def list_products(
    service: InventoryService = Depends(provide_inventory_service),
):
    return await service.list_products()

@router.get(
    "/products/{id}",
    response_model=ProductResponse,
    dependencies=[Depends(require_permission("product:view"))],
)

async def get_product(
    id: int,
    service: InventoryService = Depends(provide_inventory_service),
):
    return await service.get_product(id)

@router.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("product:create"))],
)
async def create_product(
    payload: ProductCreate,
    service: InventoryService = Depends(provide_inventory_service),
):
    return await service.create_product(
        name=payload.name,
        sku=payload.sku,
        category_id=payload.category_id,
    )

@router.patch(
    "/products/{id}",
    response_model=ProductResponse,
    dependencies=[Depends(require_permission("product:update"))],
)
async def update_product(
    id: int,
    payload: ProductUpdate,
    service: InventoryService = Depends(provide_inventory_service),
):
    return await service.update_product(
        product_id=id,
        name=payload.name,
        sku=payload.sku,
    )

@router.delete(
    "/products/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("product:deactivate"))],
)
async def delete_product(
    id: int,
    service: InventoryService = Depends(provide_inventory_service),
):
    await service.deactivate_product(id)

@router.post(
    "/products/{id}/activate",
    response_model=ProductResponse,
    dependencies=[Depends(require_permission("product:activate"))],
)
async def activate_product(
    id: int,
    service: InventoryService = Depends(provide_inventory_service),
):
    return await service.activate_product(id)
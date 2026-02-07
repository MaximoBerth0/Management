"""
GET    /inventory/products
GET    /inventory/products/{id}
POST   /inventory/products
PATCH  /inventory/products/{id}
DELETE /inventory/products/{id}

POST /inventory/stock/in
POST /inventory/stock/out
POST /inventory/stock/reserve
POST /inventory/stock/release
POST /inventory/stock/adjust

GET    /inventory/reservations
GET    /inventory/reservations/{id}
POST   /inventory/reservations
PATCH  /inventory/reservations/{id}
DELETE /inventory/reservations/{id}

"""
from typing import List

from fastapi import APIRouter, Depends, status

from app.inventory.dependencies import provide_inventory_service
from app.inventory.schemas.command import CreateProductCommand, UpdateProductCommand
from app.inventory.schemas.request import CreateProductIn, UpdateProductIn
from app.inventory.schemas.responses import ProductOut
from app.inventory.service import InventoryService
from app.rbac.dependencies import require_permission

router = APIRouter(
    prefix="/inventory",
    tags=["INVENTORY"],
)


@router.get(
    "/products",
    response_model=List[ProductOut],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission("products:view"))],
)
async def list_products(
    service: InventoryService = Depends(provide_inventory_service),
):
    return await service.list_products()


@router.get(
    "/products/{product_id}",
    response_model=ProductOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission("products:view"))],
)
async def get_product(
    product_id: int,
    service: InventoryService = Depends(provide_inventory_service),
):
    return await service.get_product(product_id=product_id)


@router.post(
    "/products",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("products:create"))],
)
async def create_product(
    data: CreateProductIn,
    service: InventoryService = Depends(provide_inventory_service),
):
    cmd = CreateProductCommand(
        name=data.name,
        sku=data.sku,
    )
    return await service.create_product(cmd)


@router.patch(
    "/products/{product_id}",
    response_model=ProductOut,
    dependencies=[Depends(require_permission("products:update"))],
)
async def update_product(
    product_id: int,
    data: UpdateProductIn,
    service: InventoryService = Depends(provide_inventory_service),
):
    cmd = UpdateProductCommand(
        product_id=product_id,
        name=data.name,
        sku=data.sku,
    )
    return await service.update_product(cmd)


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("products:deactivate"))],
)
async def delete_product(
    product_id: int,
    service: InventoryService = Depends(provide_inventory_service),
):
    await service.deactivate_product(product_id=product_id)
    return












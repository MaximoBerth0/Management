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
from app.inventory.models.enums import StockMovementType
from app.inventory.schemas.command import (
    ConfirmReservationCommand,
    CreateProductCommand,
    CreateReservationCommand,
    CreateStockMovementCommand,
    ReleaseReservationCommand,
    UpdateProductCommand,
)
from app.inventory.schemas.request import (
    ConfirmReservationIn,
    CreateProductIn,
    ReleaseReservationIn,
    StockAdjustIn,
    StockInIn,
    StockOutIn,
    StockReserveIn,
    UpdateProductIn,
)
from app.inventory.schemas.responses import (
    ProductOut,
    StockOperationOut,
    StockReservationOut,
)
from app.inventory.service import InventoryService
from app.rbac.dependencies import require_permission
from app.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)

# products

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

# stock

@router.post(
    "/stock/in",
    response_model=StockOperationOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("stock:create"))],
)
async def stock_in(
    data: StockInIn,
    service: InventoryService = Depends(provide_inventory_service),
    current_user=Depends(get_current_user),
):
    cmd = CreateStockMovementCommand(
        product_id=data.product_id,
        location_id=data.location_id,
        quantity=data.quantity,
        type=StockMovementType.IN,
        reason=data.reason,
    )

    return await service.create_stock_movement(
        cmd,
        user_id=current_user.id,
    )


@router.post(
    "/stock/out",
    response_model=StockOperationOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("stock:out"))],
)
async def stock_out(
    data: StockOutIn,
    service: InventoryService = Depends(provide_inventory_service),
    current_user=Depends(get_current_user),
):
    cmd = CreateStockMovementCommand(
        product_id=data.product_id,
        location_id=data.location_id,
        quantity=data.quantity,
        type=StockMovementType.OUT,
        reason=data.reason,
    )

    return await service.create_stock_movement(
        cmd,
        user_id=current_user.id,
    )


@router.post(
    "/stock/adjust",
    response_model=StockOperationOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("stock:adjust"))],
)
async def stock_adjust(
    data: StockAdjustIn,
    service: InventoryService = Depends(provide_inventory_service),
    current_user=Depends(get_current_user),
):
    cmd = CreateStockMovementCommand(
        product_id=data.product_id,
        location_id=data.location_id,
        quantity=data.quantity,
        type=StockMovementType.ADJUST,
        reason=data.reason,
    )

    return await service.create_stock_movement(
        cmd,
        user_id=current_user.id,
    )


@router.post(
    "/stock/reserve",
    response_model=StockReservationOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("stock:reserve"))],
)
async def reserve_stock(
    data: StockReserveIn,
    service: InventoryService = Depends(provide_inventory_service),
    current_user=Depends(get_current_user),
):
    cmd = CreateReservationCommand(
        product_id=data.product_id,
        location_id=data.location_id,
        quantity=data.quantity,
        user_id=current_user.id,
    )

    return await service.create_reservation(cmd)


@router.post(
    "/stock/release",
    response_model=StockReservationOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission("stock:release"))],
)
async def release_reservation(
    data: ReleaseReservationIn,
    service: InventoryService = Depends(provide_inventory_service),
):
    cmd = ReleaseReservationCommand(
        reservation_id=data.reservation_id,
        reason=data.reason,
    )

    return await service.release_reservation(cmd)


@router.post(
    "/stock/confirm",
    response_model=StockReservationOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission("stock:confirm"))],
)
async def confirm_reservation(
    data: ConfirmReservationIn,
    service: InventoryService = Depends(provide_inventory_service),
):
    cmd = ConfirmReservationCommand(
        reservation_id=data.reservation_id,
    )

    return await service.confirm_reservation(cmd)

















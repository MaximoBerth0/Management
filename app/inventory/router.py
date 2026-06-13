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

POST   /inventory/stock/new                            - create stock
POST   /inventory/stock/in                             - add stock
POST   /inventory/stock/out                            - remove stock
POST   /inventory/stock/adjust                         - adjust stock
GET    /inventory/stock/movements                      - list stock movements
GET    /inventory/stock?location_id&product_id&low_stock    - get current stock levels

GET    /inventory/locations                            - list locations
POST   /inventory/locations                            - create location

"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.auth.dependencies import get_current_user
from app.inventory.dependencies import provide_inventory_service
from app.inventory.schemas import (
    AddProductToCategory,
    CategoryCreate,
    CategoryResponse,
    LocationCreate,
    LocationListResponse,
    LocationResponse,
    ProductCreate,
    ProductListItemResponse,
    ProductResponse,
    ProductUpdate,
    RemoveProducFromCategory,
    StockInitialize,
    StockListResponse,
    StockMovementListResponse,
    StockMovementResponse,
    StockResponse,
    StockTransaction,
)
from app.inventory.service import InventoryService
from app.rbac.dependencies import require_permission
from app.users.model import User

logger = logging.getLogger(__name__)

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
    logger.info("create_product endpoint called", extra={
        "product_name": payload.name,
        "sku": payload.sku,
        "category_id": payload.category_id,
    })
    result = await service.create_product(
        name=payload.name,
        sku=payload.sku,
        category_id=payload.category_id,
    )

    logger.info("create_product endpoint succeeded", extra={"product_id": result.id})
    return result


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
    logger.info("update_product endpoint called", extra={"product_id": id})
    result = await service.update_product(
        product_id=id,
        name=payload.name,
        sku=payload.sku,
    )

    logger.info("update_product endpoint succeeded", extra={"product_id": id})
    return result


@router.delete(
    "/products/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("product:deactivate"))],
)
async def delete_product(
    id: int,
    service: InventoryService = Depends(provide_inventory_service),
):
    logger.info("delete_product endpoint called", extra={"product_id": id})
    await service.deactivate_product(id)
    logger.info("delete_product endpoint succeeded", extra={"product_id": id})


@router.post(
    "/products/{id}/activate",
    response_model=ProductResponse,
    dependencies=[Depends(require_permission("product:activate"))],
)
async def activate_product(
    id: int,
    service: InventoryService = Depends(provide_inventory_service),
):
    logger.info("activate_product endpoint called", extra={"product_id": id})
    result = await service.activate_product(id)
    logger.info("activate_product endpoint succeeded", extra={"product_id": id})
    return result


# categories


@router.post(
    "/categories",
    status_code=status.HTTP_201_CREATED,
    response_model=CategoryResponse,
    dependencies=[Depends(require_permission("category:create"))],
)
async def create_category(
    payload: CategoryCreate,
    service: InventoryService = Depends(provide_inventory_service),
):
    logger.info("create_category endpoint called", extra={"category_name": payload.name})
    result = await service.create_category(
        name=payload.name, description=payload.description
    )
    logger.info("create_category endpoint succeeded", extra={"category_id": result.id})
    return result


@router.delete(
    "/categories/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("category:delete"))],
)
async def delete_category(
    id: int, service: InventoryService = Depends(provide_inventory_service)
):
    logger.info("delete_category endpoint called", extra={"category_id": id})
    await service.delete_category(id)
    logger.info("delete_category endpoint succeeded", extra={"category_id": id})


@router.post(
    "/categories/{category_id}/products",
    response_model=CategoryResponse,
    dependencies=[Depends(require_permission("category:create"))],
)
async def add_product_to_category(
    category_id: int,
    payload: AddProductToCategory,
    service: InventoryService = Depends(provide_inventory_service),
):
    logger.info("add_product_to_category endpoint called", extra={"category_id": category_id, "product_id": payload.product_id})
    category = await service.add_product_to_category(payload.product_id, category_id)
    logger.info("add_product_to_category endpoint succeeded", extra={"category_id": category_id, "product_id": payload.product_id})
    return category


@router.delete(
    "/categories/{category_id}/products",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("category:remove"))],
)
async def remove_product_from_category(
    category_id: int,
    payload: RemoveProducFromCategory,
    service: InventoryService = Depends(provide_inventory_service),
):
    logger.info("remove_product_from_category endpoint called", extra={"category_id": category_id, "product_id": payload.product_id})
    await service.remove_product_from_category(payload.product_id, category_id)
    logger.info("remove_product_from_category endpoint succeeded", extra={"category_id": category_id, "product_id": payload.product_id})


# stock


@router.post(
    "/new",
    response_model=StockResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("stock:create"))],
)
async def create_stock(
    payload: StockInitialize,
    service: InventoryService = Depends(provide_inventory_service),
):
    logger.info("create_stock endpoint called", extra={
        "product_id": payload.product_id,
        "location_id": payload.location_id,
        "quantity": payload.quantity,
    })
    result = await service.initialize_stock(
        location_id=payload.location_id,
        product_id=payload.product_id,
        quantity=payload.quantity,
        reorder_point=payload.reorder_point,
    )
    logger.info("create_stock endpoint succeeded", extra={"stock_id": result.id})
    return result


@router.post(
    "/in",
    response_model=StockMovementResponse,
    dependencies=[Depends(require_permission("stock:in"))],
)
async def add_stock(
    payload: StockTransaction,
    current_user: User = Depends(get_current_user),
    service: InventoryService = Depends(provide_inventory_service),
):
    logger.info("add_stock endpoint called", extra={
        "product_id": payload.product_id,
        "location_id": payload.location_id,
        "quantity": payload.quantity,
        "user_id": current_user.id,
    })
    result = await service.add_stock(
        product_id=payload.product_id,
        location_id=payload.location_id,
        quantity=payload.quantity,
        user_id=current_user.id,
    )
    logger.info("add_stock endpoint succeeded", extra={"movement_id": result.id})
    return result


@router.post(
    "/out",
    response_model=StockMovementResponse,
    dependencies=[Depends(require_permission("stock:out"))],
)
async def remove_stock(
    payload: StockTransaction,
    current_user: User = Depends(get_current_user),
    service: InventoryService = Depends(provide_inventory_service),
):
    logger.info("remove_stock endpoint called", extra={
        "product_id": payload.product_id,
        "location_id": payload.location_id,
        "quantity": payload.quantity,
        "user_id": current_user.id,
    })
    result = await service.remove_stock(
        product_id=payload.product_id,
        location_id=payload.location_id,
        quantity=payload.quantity,
        user_id=current_user.id,
    )
    logger.info("remove_stock endpoint succeeded", extra={"movement_id": result.id})
    return result


@router.post(
    "/adjust",
    response_model=StockMovementResponse,
    dependencies=[Depends(require_permission("stock:adjust"))],
)
async def adjust_stock(
    payload: StockTransaction,
    current_user: User = Depends(get_current_user),
    service: InventoryService = Depends(provide_inventory_service),
):
    logger.info("adjust_stock endpoint called", extra={
        "product_id": payload.product_id,
        "location_id": payload.location_id,
        "quantity": payload.quantity,
        "user_id": current_user.id,
    })
    result = await service.adjust_stock(
        product_id=payload.product_id,
        location_id=payload.location_id,
        quantity=payload.quantity,
        user_id=current_user.id,
    )
    logger.info("adjust_stock endpoint succeeded", extra={"movement_id": result.id})
    return result


@router.get(
    "/movements",
    response_model=StockMovementListResponse,
    dependencies=[Depends(require_permission("stock:view"))],
)
async def list_movements(
    stock_id: int = Query(..., gt=0),
    limit: int = Query(100, ge=1, le=1000),
    service: InventoryService = Depends(provide_inventory_service),
):
    movements = await service.list_stock_movements(stock_id=stock_id, limit=limit)
    return StockMovementListResponse(items=list(movements), total=len(movements))



@router.get(
    "/stock",
    response_model=StockListResponse,
    dependencies=[Depends(require_permission("stock:view"))],
)
async def get_stock_levels(
    location_id: Optional[int] = Query(None, gt=0),
    product_id: Optional[int] = Query(None, gt=0),
    low_stock: Optional[bool] = Query(None),
    service: InventoryService = Depends(provide_inventory_service),
):
    logger.info("get_stock_levels endpoint called", extra={
        "location_id": location_id,
        "product_id": product_id,
        "low_stock": low_stock,
    })
    stocks = await service.get_stock_levels(
        location_id=location_id, product_id=product_id, low_stock=low_stock
    )

    logger.info("get_stock_levels endpoint succeeded", extra={"total": len(stocks)})
    return StockListResponse(items=list(stocks), total=len(stocks))


# location


@router.get(
    "/locations",
    response_model=LocationListResponse,
    dependencies=[Depends(require_permission("location:list"))],
)
async def get_location_list(
    service: InventoryService = Depends(provide_inventory_service),
):
    logger.info("get_location_list endpoint called")
    locations = await service.get_location_list()

    logger.info("get_location_list endpoint succeeded", extra={"total": len(locations)})
    return LocationListResponse(items=list(locations), total=len(locations))


@router.post(
    "/locations",
    status_code=status.HTTP_201_CREATED,
    response_model=LocationResponse,
    dependencies=[Depends(require_permission("location:create"))],
)
async def create_location(
    payload: LocationCreate,
    service: InventoryService = Depends(provide_inventory_service),
):
    logger.info("create_location endpoint called", extra={"location_name": payload.name})
    result = await service.create_location(
        name=payload.name, city=payload.city, address=payload.address
    )
    logger.info("create_location endpoint succeeded", extra={"location_id": result.id})
    return result
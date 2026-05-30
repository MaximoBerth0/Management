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

"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import get_current_user
from app.inventory.dependencies import provide_inventory_service
from app.inventory.schemas import (
    AddProductToCategory,
    CategoryCreate,
    CategoryResponse,
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


# categories


@router.post(
    "/categories",
    response_model=CategoryResponse,
    dependencies=[Depends(require_permission("category:create"))],
)
async def create_category(
    payload: CategoryCreate,
    service: InventoryService = Depends(provide_inventory_service),
):
    return await service.create_category(
        name=payload.name, description=payload.description
    )


@router.delete(
    "/categories/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("category:delete"))],
)
async def delete_category(
    id: int, service: InventoryService = Depends(provide_inventory_service)
):
    await service.delete_category(id)


@router.post(
    "categories/{category_id}/products",
    response_model=CategoryResponse,
    dependencies=[Depends(require_permission("category:create"))],
)
async def add_product_to_category(
    category_id: int,
    payload: AddProductToCategory,
    service: InventoryService = Depends(provide_inventory_service),
):
    await service.add_product_to_category(payload.product_id, category_id)


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
    await service.remove_product_from_category(payload.product_id, category_id)


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
    return await service.initialize_stock(
        location_id=payload.location_id,
        product_id=payload.product_id,
        quantity=payload.quantity,
        reorder_point=payload.reorder_point,
    )


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
    return await service.add_stock(
        product_id=payload.product_id,
        location_id=payload.location_id,
        quantity=payload.quantity,
        user_id=current_user.id,
    )


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
    return await service.remove_stock(
        product_id=payload.product_id,
        location_id=payload.location_id,
        quantity=payload.quantity,
        user_id=current_user.id,
    )


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
    return await service.adjust_stock(
        product_id=payload.product_id,
        location_id=payload.location_id,
        quantity=payload.quantity,
        user_id=current_user.id,
    )


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
    try:
        movements = await service.list_stock_movements(stock_id=stock_id, limit=limit)
        return StockMovementListResponse(items=list(movements), total=len(movements))

    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


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
    stocks = await service.get_stock_levels(
        location_id=location_id, product_id=product_id, low_stock=low_stock
    )

    return StockListResponse(items=list(stocks), total=len(stocks))

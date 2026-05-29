from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.orders.dependencies import get_order_service
from app.orders.schemas import AddItemRequest, ConfirmOrderRequest, OrderResponse
from app.orders.service import OrderService
from app.rbac.dependencies import require_permission
from app.users.models import User

"""
POST /orders                             - create order
POST /orders/{id}/items                  - add item to order
DELETE /orders/{id}/items/{item_id}      - remove item from order

# state transitions
PATCH /orders/{id}/confirm               - confirm order
PATCH /orders/{id}/cancel                - cancel order
PATCH /orders/{id}/complete              - complete order
"""

router = APIRouter(prefix="orders/", tags=["ORDERS"])

# orders


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("order:create"))],
)
async def create_order(
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    order = await service.create_order(user_id=current_user.id)
    return order


@router.post(
    "/{id}/items",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission("order:add"))],
)
async def add_item_to_order(
    id: int,
    payload: AddItemRequest,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    try:
        order = await service.add_item_to_order(
            order_id=id,
            product_id=payload.product_id,
            quantity=payload.quantity,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    return order


@router.delete(
    "/{order_id}/items/{product_id}",
    response_model=OrderResponse,
    dependencies=[Depends(require_permission("order:remove"))],
)
async def remove_item_from_order(
    order_id: int,
    product_id: int,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    try:
        order = await service.remove_item_from_order(
            order_id=order_id,
            product_id=product_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    return order


# state transitions


@router.patch(
    "/{id}/confirm",
    response_model=OrderResponse,
    dependencies=[Depends(require_permission("order:confirm"))],
)
async def confirm_order(
    id: int,
    payload: ConfirmOrderRequest,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    try:
        order = await service.confirm_order(
            order_id=id,
            location_id=payload.location_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    return order


@router.patch(
    "/{id}/cancel",
    response_model=OrderResponse,
    dependencies=[Depends(require_permission("order:cancel"))],
)
async def cancel_order(
    id: int,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    try:
        order = await service.cancel_order(order_id=id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    return order


@router.patch(
    "/{id}/complete",
    response_model=OrderResponse,
    dependencies=[Depends(require_permission("order:complete"))],
)
async def complete_order(
    id: int,
    service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    try:
        order = await service.complete_order(order_id=id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    return order

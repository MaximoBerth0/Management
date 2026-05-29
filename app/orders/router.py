from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.orders.dependencies import get_order_service
from app.orders.models.order import Order
from app.orders.schemas import AddItemRequest, OrderResponse
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

router = APIRouter(
    prefix="orders/",
    tags=["ORDERS"]
)

# orders

@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("order:create"))]
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
    dependencies=[Depends(require_permission("order:add"))]
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
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("order:remove"))]
)
async def remove_item_from_order(self, order_id: int, product_id: int) -> Order:
    order = await self.order_repo.remove_item(order_id, product_id)
    if order is None:
        raise ValueError("Order not found")
    return order
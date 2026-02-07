
"""
PRODUCT:
get_product()
list_products()
create_product()
deactivate_product()
update_product()

STOCK:
create_stock_movement()

RESERVATION:
create_reservation()
release_reservation()
confirm_reservation()

to be added in the future:
- list reservations
"""

from typing import List, Optional

from app.core.unit_of_work import UnitOfWork
from app.inventory.models.inventory_model import (
    Product,
    StockMovement,
    StockMovementType,
    StockReservation,
    StockReservationStatus,
)
from app.inventory.repositories.product_repo import ProductRepository
from app.inventory.repositories.stock_inventory_repo import StockInventoryRepository
from app.inventory.schemas.command import (
    ConfirmReservationCommand,
    CreateProductCommand,
    CreateReservationCommand,
    CreateStockMovementCommand,
    ProductDTO,
    ReleaseReservationCommand,
    ReservationDTO,
    StockMovementDTO,
    UpdateProductCommand,
)
from app.shared.exceptions.inventory_errors import (
    InsufficientStock,
    ProductAlreadyExists,
    ProductAlreadyInactive,
    ProductNotFound,
    ProductSkuAlreadyExists,
    ReservationInactive,
)


#internal helper
def to_product_dto(product: Product) -> ProductDTO:
    return ProductDTO(
        id=product.id,
        name=product.name,
        sku=product.sku,
        is_active=bool(product.is_active),
    )


class InventoryService:
    def __init__(
        self,
        product_repo: ProductRepository,
        stock_inventory_repo: StockInventoryRepository,
        uow: UnitOfWork,
    ):
        self.product_repo = product_repo
        self.stock_inventory_repo = stock_inventory_repo
        self.uow = uow

# Product

    async def get_product(self, *, product_id: int) -> ProductDTO:
        async with self.uow:
            product = await self.product_repo.get_by_id(product_id)

            if not product:
                raise ProductNotFound()

            return to_product_dto(product)

    async def create_product(self, cmd: CreateProductCommand):
        async with self.uow:
            if await self.product_repo.get_by_sku(cmd.sku):
                raise ProductAlreadyExists()

            product = Product(
                name=cmd.name,
                sku=cmd.sku,
            )

            await self.product_repo.create(product)

            return to_product_dto(product)

    async def deactivate_product(self, *, product_id: int) -> None:
        async with self.uow:
            product = await self.product_repo.get_by_id(product_id)

            if not product:
                raise ProductNotFound()

            if not product.is_active:
                raise ProductAlreadyInactive()

            product.is_active = False

    async def update_product(
            self,
            cmd: UpdateProductCommand,
    ) -> ProductDTO:
        async with self.uow:

            product = await self.product_repo.get_by_id(cmd.product_id)

            if not product:
                raise ProductNotFound()

            if not product.is_active:
                raise ProductAlreadyInactive()

            if cmd.name is not None:
                product.name = cmd.name

            if cmd.sku is not None and cmd.sku != product.sku:
                if await self.product_repo.get_by_sku(cmd.sku):
                    raise ProductSkuAlreadyExists()
                product.sku = cmd.sku

            return to_product_dto(product)

    async def list_products(
            self,
            *,
            is_active: Optional[bool] = None,
    ) -> List[ProductDTO]:
        async with self.uow:
            products = await self.product_repo.list(
                is_active=is_active
            )

            return [
                to_product_dto(product)
                for product in products
            ]

    async def create_stock_movement(
        self,
        cmd: CreateStockMovementCommand,
        *,
        user_id: int | None = None,
    ) -> StockMovementDTO:
        async with self.uow:

            stock = await self.stock_inventory_repo.get_for_update(
                product_id=cmd.product_id,
                location_id=cmd.location_id,
            )

            match cmd.type:

                case StockMovementType.IN:
                    stock.quantity_available += cmd.quantity

                case StockMovementType.OUT:
                    if stock.quantity_available < cmd.quantity:
                        raise InsufficientStock()
                    stock.quantity_available -= cmd.quantity

                case StockMovementType.RESERVE:
                    if stock.quantity_available < cmd.quantity:
                        raise InsufficientStock()
                    stock.quantity_available -= cmd.quantity
                    stock.quantity_reserved += cmd.quantity

                case StockMovementType.RELEASE:
                    if stock.quantity_reserved < cmd.quantity:
                        raise InsufficientStock()
                    stock.quantity_reserved -= cmd.quantity
                    stock.quantity_available += cmd.quantity

                case StockMovementType.ADJUST:
                    stock.quantity_available = cmd.quantity
                    stock.quantity_reserved = 0

                case _:
                    raise ValueError("Invalid stock movement type")

            await self.stock_inventory_repo.save(stock)

            movement = StockMovement(
                stock=stock,
                type=cmd.type,
                quantity=cmd.quantity,
                reason=cmd.reason,
                created_by_user_id=user_id,
            )

            await self.stock_inventory_repo.add_movement(movement)

            return StockMovementDTO(
                id=movement.id,
                product_id=stock.product_id,
                location_id=stock.location_id,
                type=movement.type,
                quantity=movement.quantity,
                reason=movement.reason,
                created_at=movement.created_at,
            )


    # Reservations

    async def create_reservation(
        self,
        cmd: CreateReservationCommand,
    ) -> ReservationDTO:
        async with self.uow:

            stock = await self.stock_inventory_repo.get_for_update(
                product_id=cmd.product_id,
                location_id=cmd.location_id,
            )

            if stock.quantity_available < cmd.quantity:
                raise InsufficientStock()

            stock.quantity_available -= cmd.quantity
            stock.quantity_reserved += cmd.quantity

            await self.stock_inventory_repo.save(stock)

            reservation = StockReservation(
                product_id=cmd.product_id,
                location_id=cmd.location_id,
                amount=cmd.quantity,
                user_id=cmd.user_id,
                status=StockReservationStatus.ACTIVE,
            )

            await self.stock_inventory_repo.add_reservation(reservation)

            movement = StockMovement(
                stock=stock,
                type=StockMovementType.RESERVE,
                quantity=cmd.quantity,
                created_by_user_id=cmd.user_id,
            )

            await self.stock_inventory_repo.add_movement(movement)

            return ReservationDTO(
                id=reservation.id,
                product_id=reservation.product_id,
                location_id=reservation.location_id,
                quantity=reservation.amount,
                status=reservation.status,
                user_id=reservation.user_id,
                created_at=reservation.created_at,
            )


    async def release_reservation(
        self,
        cmd: ReleaseReservationCommand,
    ) -> ReservationDTO:
        async with self.uow:

            reservation = await self.stock_inventory_repo.get_reservation_for_update(
                reservation_id=cmd.reservation_id,
            )

            if reservation.status != StockReservationStatus.ACTIVE:
                raise ReservationInactive()

            stock = await self.stock_inventory_repo.get_for_update(
                product_id=reservation.product_id,
                location_id=reservation.location_id,
            )

            if stock.quantity_reserved < reservation.amount:
                raise InsufficientStock()

            stock.quantity_reserved -= reservation.amount
            stock.quantity_available += reservation.amount

            reservation.status = StockReservationStatus.RELEASED

            await self.stock_inventory_repo.save(stock)

            movement = StockMovement(
                stock=stock,
                type=StockMovementType.RELEASE,
                quantity=reservation.amount,
                reason=cmd.reason,
                created_by_user_id=reservation.user_id,
            )

            await self.stock_inventory_repo.add_movement(movement)

            return ReservationDTO(
                id=reservation.id,
                product_id=reservation.product_id,
                location_id=reservation.location_id,
                quantity=reservation.amount,
                status=StockReservationStatus(reservation.status),
                user_id=reservation.user_id,
                created_at=reservation.created_at,
            )


    async def confirm_reservation(
        self,
        cmd: ConfirmReservationCommand,
    ) -> ReservationDTO:
        async with self.uow:

            reservation = await self.stock_inventory_repo.get_reservation_for_update(
                reservation_id=cmd.reservation_id,
            )

            if reservation.status != StockReservationStatus.ACTIVE:
                raise ReservationInactive()

            stock = await self.stock_inventory_repo.get_for_update(
                product_id=reservation.product_id,
                location_id=reservation.location_id,
            )

            if stock.quantity_reserved < reservation.amount:
                raise InsufficientStock()

            stock.quantity_reserved -= reservation.amount
            reservation.status = StockReservationStatus.CONFIRMED

            await self.stock_inventory_repo.save(stock)

            movement = StockMovement(
                stock=stock,
                type=StockMovementType.OUT,
                quantity=reservation.amount,
                reason="Reservation confirmed",
                created_by_user_id=reservation.user_id,
            )

            await self.stock_inventory_repo.add_movement(movement)

            return ReservationDTO(
                id=reservation.id,
                product_id=reservation.product_id,
                location_id=reservation.location_id,
                quantity=reservation.amount,
                status=StockReservationStatus(reservation.status),
                user_id=reservation.user_id,
                created_at=reservation.created_at,
            )

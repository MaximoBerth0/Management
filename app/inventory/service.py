"""
PRODUCT:
  get_product()
  list_products()
  create_product()
  update_product()
  activate_product()
  deactivate_product()

CATEGORY:
  create_category()
  remove_category()
  add_product_to_category()
  remove_product_from_category

STOCK:
  initialize_stock()
  add_stock()
  remove_stock()
  adjust_stock()
  list_stock_movements()
  get_stock_levels()

RESERVATION:
  reserve_for_item()
  release_for_item()
  fulfill_for_item()

"""

from typing import Optional

from app.inventory.exceptions import (
    CategoryAlreadyExists,
    CategoryDescriptionIsRequired,
    CategoryNameIsRequired,
    CategoryNotFound,
    InsufficientStock,
    InvalidLocation,
    InvalidProductOrLocation,
    InvalidQuantityStock,
    InvalidReservationStatus,
    NoParametersProvide,
    ProductAlreadyExits,
    ProductNameIsRequired,
    ProductNotFound,
    ReservationNotFound,
    SKUIsRequired,
    StockNegative,
    StockNotFound,
)
from app.inventory.models.enums import ReservationStatus, StockMovementType
from app.inventory.models.reservation import StockReservation
from app.inventory.models.stock import InventoryStock, StockMovement
from app.inventory.repositories.category_repo import CategoryRepository
from app.inventory.repositories.location_repo import LocationRepository
from app.inventory.repositories.product_repo import ProductRepository
from app.inventory.repositories.reservation_repo import ReservationRepository
from app.inventory.repositories.stock_repo import StockRepository


class InventoryService:
    def __init__(
        self,
        stock_repo: StockRepository,
        product_repo: ProductRepository,
        category_repo: CategoryRepository,
        location_repo: LocationRepository,
        reservation_repo: ReservationRepository,
    ):
        self.stock_repo = stock_repo
        self.product_repo = product_repo
        self.category_repo = category_repo
        self.location_repo = location_repo
        self.reservation_repo = reservation_repo

    # product

    async def get_product(self, product_id: int):
        result = self.product_repo.get_product(product_id)
        if result is None:
            return ProductNotFound()
        return result

    async def list_products(self):
        result = self.product_repo.list_products()
        return result

    async def create_product(self, name: str, sku: str, category_id: int):
        if not name or not name.strip():
            raise ProductNameIsRequired()

        if not sku or not sku.strip():
            raise SKUIsRequired()

        # normalize
        name = name.strip()
        sku = sku.strip().upper()

        existing = await self.product_repo.get_by_sku(sku)
        if existing:
            raise ProductAlreadyExits()

        category_exists = await self.category_repo.get_category(category_id)
        if category_exists:
            raise CategoryAlreadyExists()

        return await self.product_repo.create_product(name, sku, category_id)

    async def update_product(
        self,
        product_id: int,
        name: str | None = None,
        sku: str | None = None,
    ):
        if name is None and sku is None:
            raise NoParametersProvide()

        if name is not None:
            name = name.strip()
            if not name:
                raise ProductNameIsRequired()

        if sku is not None:
            sku = sku.strip().upper()
            if not sku:
                raise SKUIsRequired()

            existing = await self.product_repo.get_by_sku(sku)
            if existing and existing.id != product_id:
                raise ProductAlreadyExits()

        product = await self.product_repo.update_product(product_id, name, sku)
        if not product:
            raise ProductNotFound()

        return product

    async def activate_product(self, product_id: int):
        activate = self.product_repo.activate_product(product_id)
        return activate

    async def deactivate_product(self, product_id):
        deactivate = self.product_repo.deactivate_product(product_id)
        return deactivate

    # category

    async def create_category(self, name: str, description: str):
        if not name or not name.strip():
            raise CategoryNameIsRequired()

        if not description or not description.strip():
            raise CategoryDescriptionIsRequired()

        name = name.strip()
        description = description.strip()

        existing = await self.category_repo.get_by_name(name)
        if existing:
            raise CategoryAlreadyExists()

        return await self.category_repo.create_category(name, description)

    async def delete_category(self, category_id: int):
        return await self.category_repo.delete_category(category_id)

    async def add_product_to_category(self, product_id: int, category_id: int):
        category = await self.category_repo.get_category(category_id)
        if not category:
            raise CategoryNotFound()

        product = await self.product_repo.get_product(product_id)

        if product not in category.products:
            category.products.append(product)
            await self.category_repo.save_category(category)

        return category

    async def remove_product_from_category(self, product_id: int, category_id: int):
        category = await self.category_repo.get_category(category_id)
        if not category:
            raise CategoryNotFound()

        product = await self.product_repo.get_product(product_id)

        return await self.category_repo.remove_product(category, product)

    # stock

    async def initialize_stock(
        self, location_id: int, product_id: int, quantity: int, reorder_point: int
    ):
        location_id = abs(int(location_id))
        product_id = abs(int(product_id))
        quantity = abs(int(quantity))
        reorder_point = abs(int(reorder_point))

        # ensure reorder_point doesn't exceed quantity
        reorder_point = min(reorder_point, quantity)

        location = await self.location_repo.get_location(location_id)
        if not location:
            raise InvalidLocation()

        await self.product_repo.get_product(product_id)

        if quantity <= 0:
            raise InvalidQuantityStock()

        return await self.stock_repo.initialize_stock(
            location_id, product_id, quantity, reorder_point
        )

    async def add_stock(self, product_id, location_id, quantity, user_id):
        stock = await self.stock_repo.get_stock_by_location_and_product_for_update(
            product_id, location_id
        )
        if not stock:
            raise InvalidProductOrLocation()

        previous_quantity = stock.quantity

        stock.quantity += quantity
        new_quantity = stock.quantity

        movement = StockMovement(
            stock_id=stock.id,
            movement_type=StockMovementType.IN,
            quantity=quantity,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            created_by=user_id,
        )
        await self.stock_repo.update_quantity_stock(stock)
        await self.stock_repo.create_movement(movement)

        return movement

    async def remove_stock(self, product_id, location_id, quantity, user_id):
        stock = await self.stock_repo.get_stock_by_location_and_product_for_update(
            product_id, location_id
        )
        if not stock:
            raise InvalidProductOrLocation()

        if stock.quantity < quantity:
            raise StockNegative()

        previous_quantity = stock.quantity

        stock.quantity -= quantity
        new_quantity = stock.quantity

        movement = StockMovement(
            stock_id=stock.id,
            movement_type=StockMovementType.OUT,
            quantity=quantity,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            created_by=user_id,
        )
        await self.stock_repo.update_quantity_stock(stock)
        await self.stock_repo.create_movement(movement)

        return movement

    async def adjust_stock(self, product_id, location_id, quantity, user_id):
        stock = await self.stock_repo.get_stock_by_location_and_product_for_update(
            product_id, location_id
        )
        if not stock:
            raise InvalidProductOrLocation()

        if quantity < 0:
            raise StockNegative()

        previous_quantity = stock.quantity
        stock.quantity = quantity
        new_quantity = stock.quantity

        movement = StockMovement(
            stock_id=stock.id,
            movement_type=StockMovementType.ADJUST,
            quantity=abs(new_quantity - previous_quantity),  # store the difference
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            created_by=user_id,
        )

        await self.stock_repo.update_quantity_stock(stock)
        await self.stock_repo.create_movement(movement)
        return movement

    async def list_stock_movements(self, stock_id: int, limit: int = 100):
        stock = await self.stock_repo.get_stock(stock_id)
        if not stock:
            raise StockNotFound()

        return await self.stock_repo.list_stock_movements(stock_id, limit)

    async def get_stock_levels(
        self,
        location_id: Optional[int] = None,
        product_id: Optional[int] = None,
        low_stock: Optional[bool] = None,
    ) -> list[InventoryStock]:

        return await self.stock_repo.get_stock_levels(
            location_id=location_id, product_id=product_id, low_stock=low_stock
        )

    # reservation

    async def reserve_for_item(
        self,
        order_item_id: int,
        product_id: int,
        location_id: int,
        quantity: int,
    ) -> StockReservation:
        if quantity <= 0:
            raise InvalidQuantityStock()

        stock = await self.stock_repo.get_stock_by_location_and_product_for_update(
            product_id=product_id,
            location_id=location_id,
        )
        if not stock:
            raise StockNotFound()

        available = stock.quantity - stock.reserved_quantity
        if available < quantity:
            raise InsufficientStock()

        stock.reserved_quantity += quantity

        return await self.reservation_repo.create_reservation(
            order_item_id=order_item_id,
            stock_id=stock.id,
            quantity=quantity,
        )

    async def release_for_item(self, reservation_id: int) -> StockReservation:
        reservation = await self.stock_repo.get_reservation_by_id(reservation_id)
        if not reservation:
            raise ReservationNotFound()

        if reservation.status != ReservationStatus.RESERVED:
            raise InvalidReservationStatus()

        stock = await self.stock_repo.get_stock_by_id_for_update(
            reservation.stock_id
        )
        if not stock:
            raise StockNotFound()

        stock.reserved_quantity -= reservation.quantity
        reservation.status = ReservationStatus.RELEASED

        return reservation

    async def fulfill_for_item(self, reservation_id: int) -> StockReservation:
        reservation = await self.stock_repo.get_reservation_by_id(reservation_id)
        if not reservation:
            raise ReservationNotFound()

        if reservation.status != ReservationStatus.RESERVED:
            raise InvalidReservationStatus()

        stock = await self.stock_repo.get_stock_by_id_for_update(
            reservation.stock_id
        )
        if not stock:
            raise StockNotFound()

        stock.quantity -= reservation.quantity
        stock.reserved_quantity -= reservation.quantity
        reservation.status = ReservationStatus.FULFILLED

        return reservation

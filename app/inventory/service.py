"""
create_product()
deactivate_product()
update_product()

create_stock_movement()
       ↑↑↑↑
create_reservation()
confirm_reservation()
release_reservation()
"""

from app.inventory.models.inventory_model import Product
from app.inventory.repositories.stock_inventory_repo import StockInventoryRepository
from app.inventory.repositories.product_repo import ProductRepository
from app.core.unit_of_work import UnitOfWork
from app.inventory.schemas.command import CreateProductCommand, ProductDTO, DeactivateProductCommand, UpdateProductCommand
from app.shared.exceptions.inventory_errors import ProductAlreadyExists, ProductNotFound, ProductAlreadyInactive, ProductSkuAlreadyExists

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

    async def create_product(self, cmd: CreateProductCommand):
        async with self.uow:
            if await self.product_repo.get_by_sku(cmd.sku):
                raise ProductAlreadyExists()

            product = Product(
                name=cmd.name,
                sku=cmd.sku,
            )

            await self.product_repo.create(product)

            return ProductDTO(
                id=product.id,
                name=product.name,
                sku=product.sku,
                is_active=product.is_active,
            )

    async def deactivate_product(self, cmd: DeactivateProductCommand):
        async with self.uow:
            product = await self.product_repo.get_by_id(cmd.product_id)

            if not product:
                raise ProductNotFound()

            if not product.is_active:
                raise ProductAlreadyInactive()

            product.is_active = False


    async def update_product(self, cmd: UpdateProductCommand):
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

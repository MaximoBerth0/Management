from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.inventory.models import Product
from sqlalchemy.sql import Select


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    #Internal helper (DRY)
    async def _one(self, stmt: Select) -> Product | None:
        result = await self.db.scalars(stmt)
        return result.first()

    # CRUD
    async def create(self, product: Product) -> Product:
        self.db.add(product)
        await self.db.flush()
        return product

    async def get_by_id(self, product_id: int) -> Product | None:
        return await self._one(
            select(Product).where(Product.id == product_id)
        )

    async def get_by_sku(self, product_sku: str) -> Product | None:
        return await self._one(
            select(Product).where(Product.sku == product_sku)
        )

    async def get_by_name(self, product_name: str) -> Product | None:
        return await self._one(
            select(Product).where(Product.name == product_name)
        )

    async def list(self) -> list[Product]:
        stmt = select(Product).where(Product.is_active_(True))
        result = await self.db.scalars(stmt)
        return result.all()

    async def update(self, product: Product) -> Product:
        self.db.add(product)
        await self.db.flush()
        return product

    async def delete(self, product: Product) -> None:
        await self.db.delete(product)
        await self.db.flush()

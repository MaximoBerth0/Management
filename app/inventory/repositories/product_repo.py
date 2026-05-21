from app.inventory.models.product import Category, Product
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_product(self, product_id: int) -> Product | None:
        stmt = select(Product).where(Product.id == product_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_products(self) -> list[Product]: 
        stmt = select(Product)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def create_product(self, name: str, sku: str, category: Category) -> Product | None:
        product = Product(name=name, sku=sku, category=category)
        await self.db.commit()
        await self.db.refresh(product)
        return product 
    
    async def update_product(
        self, 
        product_id: int,
        name: str | None = None,
        sku: str | None = None
    ) -> Product | None:
        stmt = select(Product).where(Product.id == product_id)
        result = await self.db.execute(stmt)
        product = result.scalar_one_or_none()
    
        if not product:
            return None
    
        if name is not None:
           product.name = name
        if sku is not None:
            product.sku = sku
    
        await self.db.commit()
        await self.db.refresh(product)
    
        return product
    
    async def activate_product(self, product_id: int) -> Product | None:
        stmt = select(Product).where(Product.id == product_id)
        result = await self.db.execute(stmt)
        product = result.scalar_one_or_none()
    
        if not product:
            return None
    
        product.is_active = True
    
    async def deactivate_product(self, product_id: int) -> Product | None: 
        stmt = select(Product).where(Product.id == product_id)
        result = await self.db.execute(stmt)
        product = result.scalar_one_or_none()
    
        if not product:
            return None
        
        product.is_active = False 

        await self.db.commit()
        await self.db.refresh(product)

        return product

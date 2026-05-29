from app.inventory.models.category import Category
from app.inventory.models.product import Product
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_category(self, category_id: int) -> Category | None:
        stmt = select(Category).where(Category.id == category_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Category | None:
        stmt = select(Category).where(Category.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_categories(self) -> list[Category]:
        stmt = select(Category)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_category(self, name: str, description: str) -> Category:
        category = Category(name=name, description=description)
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def save_category(self, category: Category) -> Category:
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def remove_product(self, category: Category, product: Product) -> Category:
        if product in category.products:
            category.products.remove(product)
            await self.db.commit()
            await self.db.refresh(category)
        return category

    async def delete_category(self, category_id: int) -> bool:
        category = await self.get_category(category_id)
        if not category:
            return False

        await self.db.delete(category)
        await self.db.commit()
        return True

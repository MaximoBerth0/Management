from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.inventory.models.reservation import StockReservation
    from app.inventory.models.stock import InventoryStock

# this is for many-to-many relationships (product-category)
product_category = Table(
    "inventory_product_categories",
    Base.metadata,
    Column("product_id", ForeignKey("inventory_products.id"), primary_key=True),
    Column("category_id", ForeignKey("inventory_categories.id"), primary_key=True),
)


class Category(Base):
    __tablename__ = "inventory_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    products: Mapped[list["Product"]] = relationship(
        secondary=product_category,
        back_populates="categories",
    )


class Product(Base):
    __tablename__ = "inventory_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    categories: Mapped[list["Category"]] = relationship(
        secondary=product_category,
        back_populates="products",
    )
    stocks: Mapped[list["InventoryStock"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    reservations: Mapped[list["StockReservation"]] = relationship(
        back_populates="product"
    )

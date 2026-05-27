from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.inventory.models.category import product_category

if TYPE_CHECKING:
    from app.inventory.models.category import Category
    from app.inventory.models.reservation import StockReservation
    from app.inventory.models.stock import InventoryStock


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

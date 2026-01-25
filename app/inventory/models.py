from enum import Enum
from sqlalchemy import String, Boolean, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SAEnum, Text
from app.database.base import Base


class StockMovementType(str, Enum):
    IN = "in"
    OUT = "out"
    ADJUST = "adjust"
    RESERVE = "reserve"
    RELEASE = "release"


class Product(Base):
    __tablename__ = "inventory_product"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    stock: Mapped["InventoryStock"] = relationship(
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
    )


class InventoryLocation(Base):
    __tablename__ = "inventory_locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    stock_items: Mapped[list["InventoryStock"]] = relationship(
        back_populates="location"
    )


class InventoryStock(Base):
    __tablename__ = "inventory_stock"
    __table_args__ = (
        CheckConstraint("quantity_available >= 0", name="ck_stock_available_non_negative"),
        CheckConstraint("quantity_reserved >= 0", name="ck_stock_reserved_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_products.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    location_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_locations.id"),
        nullable=False,
    )

    quantity_available: Mapped[int] = mapped_column(Integer, default=0)
    quantity_reserved: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped["Product"] = relationship(back_populates="stock")
    location: Mapped["InventoryLocation"] = relationship(back_populates="stock_items")
    movements: Mapped[list["StockMovement"]] = relationship(
        back_populates="stock",
        cascade="all, delete-orphan",
    )


class StockMovement(Base):
    __tablename__ = "inventory_stock_movements"

    id: Mapped[int] = mapped_column(primary_key=True)

    stock_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_stock.id", ondelete="CASCADE"),
        nullable=False,
    )

    type: Mapped[StockMovementType] = mapped_column(
        SAEnum(StockMovementType, name="stock_movement_type"),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)

    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    stock: Mapped["InventoryStock"] = relationship(back_populates="movements")
from enum import Enum
from datetime import datetime

from sqlalchemy import (
    String,
    Boolean,
    Integer,
    ForeignKey,
    CheckConstraint,
    DateTime,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SAEnum, Text

from app.database.base import Base


# enums (It's only used in databases)

class StockMovementType(str, Enum):
    IN = "in"
    OUT = "out"
    ADJUST = "adjust"
    RESERVE = "reserve"
    RELEASE = "release"


class StockReservationStatus(str, Enum):
    ACTIVE = "active"
    RELEASED = "released"
    CONFIRMED = "confirmed"


# product

class Product(Base):
    __tablename__ = "inventory_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    stock: Mapped["InventoryStock"] = relationship(
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan",
    )

    reservations: Mapped[list["StockReservation"]] = relationship(
        back_populates="product"
    )


# location (There's one for now)

class InventoryLocation(Base):
    __tablename__ = "inventory_locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    stock_items: Mapped[list["InventoryStock"]] = relationship(
        back_populates="location"
    )


# stock

class InventoryStock(Base):
    __tablename__ = "inventory_stock"
    __table_args__ = (
        CheckConstraint(
            "quantity_available >= 0",
            name="ck_stock_available_non_negative",
        ),
        CheckConstraint(
            "quantity_reserved >= 0",
            name="ck_stock_reserved_non_negative",
        ),
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


# stock movement

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

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    stock: Mapped["InventoryStock"] = relationship(back_populates="movements")


# reservations

class StockReservation(Base):
    __tablename__ = "inventory_reservations"

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_products.id", ondelete="CASCADE"),
        nullable=False,
    )

    amount: Mapped[int] = mapped_column(nullable=False)

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    status: Mapped[StockReservationStatus] = mapped_column(
        SAEnum(StockReservationStatus, name="stock_reservation_status"),
        default=StockReservationStatus.ACTIVE,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    product: Mapped["Product"] = relationship(back_populates="reservations")

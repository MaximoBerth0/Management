from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.inventory.models.enums import StockMovementType

if TYPE_CHECKING:
    from app.inventory.models.location import Location
    from app.inventory.models.product import Product
    from app.inventory.models.reservation import StockReservation
    from app.users.model import User


class InventoryStock(Base):
    __tablename__ = "inventory_stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_location.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_products.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reserved_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # trigger alert
    reorder_point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    location: Mapped["Location"] = relationship(back_populates="stocks")
    product: Mapped["Product"] = relationship(back_populates="stocks")
    movements: Mapped[list["StockMovement"]] = relationship(
        back_populates="stock", cascade="all, delete-orphan"
    )
    reservations: Mapped[list["StockReservation"]] = relationship(
        back_populates="stock"
    )


class StockMovement(Base):
    __tablename__ = "inventory_stock_movement"

    id: Mapped[int] = mapped_column(primary_key=True)
    movement_type: Mapped[StockMovementType] = mapped_column(
        SAEnum(StockMovementType), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_stock.id"), nullable=False
    )

    # audit fields
    previous_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    new_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    stock: Mapped["InventoryStock"] = relationship(back_populates="movements")
    created_by_user: Mapped["User"] = relationship(foreign_keys=[created_by])

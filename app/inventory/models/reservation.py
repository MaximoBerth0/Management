from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.inventory.models.enums import ReservationStatus
from app.inventory.models.stock import InventoryStock
from app.orders.models.order import OrderItem


class StockReservation(Base):
    __tablename__ = "stock_reservation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    order_item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("order_items.id"),
        nullable=False,
        unique=True,
    )

    stock_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("inventory_stock.id"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[ReservationStatus] = mapped_column(
        Enum(ReservationStatus),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    order_item: Mapped["OrderItem"] = relationship(back_populates="reservation")
    stock: Mapped["InventoryStock"] = relationship(back_populates="reservations")

    @classmethod
    def create(
        cls, order_item_id: int, stock_id: int, quantity: int
    ) -> "StockReservation":
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        return cls(
            order_item_id=order_item_id,
            stock_id=stock_id,
            quantity=quantity,
            status=ReservationStatus.RESERVED,
        )

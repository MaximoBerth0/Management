from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.orders.models.enums import ReservationStatus


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

from datetime import datetime, timezone
from typing import List

from sqlalchemy import DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.orders.models.enums import OrderStatus
from app.database.base import Base
from app.shared.exceptions.order_errors import InvalidOrderStateError


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )

    @classmethod
    def create(cls, user_id: int) -> "Order":
        return cls(
            user_id=user_id,
            status=OrderStatus.CREATED,
        )

    def add_item(self, product_id: int, quantity: int):
        if self.status != OrderStatus.CREATED:
            raise InvalidOrderStateError(
                "Cannot modify order in current state"
            )

        item = OrderItem(
            product_id=product_id,
            quantity=quantity,
        )

        self.items.append(item)

    def confirm(self):
        if self.status != OrderStatus.CREATED:
            raise InvalidOrderStateError(
                "Only created orders can be confirmed"
            )

        self.status = OrderStatus.CONFIRMED

    def cancel(self):
        if self.status not in {
            OrderStatus.CREATED,
            OrderStatus.CONFIRMED,
        }:
            raise InvalidOrderStateError(
                "Cannot cancel this order"
            )

        self.status = OrderStatus.CANCELLED

    def complete(self):
        if self.status != OrderStatus.CONFIRMED:
            raise InvalidOrderStateError(
                "Only confirmed orders can be completed"
            )

        self.status = OrderStatus.COMPLETED


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    order: Mapped["Order"] = relationship(
        back_populates="items",
    )

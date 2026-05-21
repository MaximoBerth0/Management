from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.inventory.models.stock import InventoryStock


class Location(Base):
    __tablename__ = "inventory_location"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(255))

    stocks: Mapped[list["InventoryStock"]] = relationship(back_populates="location")

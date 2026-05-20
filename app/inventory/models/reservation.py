"""
StockReservation
"""

from app.database.base import Base


class StockReservation(Base):
    __tablename__ = "inventory_stock_reservation"
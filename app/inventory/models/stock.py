
"""
InventoryStock
StockMovement
"""

from app.database.base import Base


class InventoryStock(Base):
    __tablename__ = "inventory_stock"

class StockMovement(Base):
    __tablename__ = "inventory_stock_movement"
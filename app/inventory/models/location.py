"""
InventoryLocation
"""

from app.database.base import Base


class Location(Base):
    __tablename__ = "inventory_location"
from enum import Enum


class StockMovementType(str, Enum):
    IN = "in"
    OUT = "out"
    ADJUST = "adjust"
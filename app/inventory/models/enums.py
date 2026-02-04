from enum import Enum


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

from enum import Enum


class StockMovementType(str, Enum):
    IN = "in"
    OUT = "out"
    ADJUST = "adjust"


class ReservationStatus(str, Enum):
    RESERVED = "reserved"
    FULFILLED = "fulfilled"
    RELEASED = "released"
    FAILED = "failed"

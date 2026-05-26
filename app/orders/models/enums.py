from enum import Enum


class OrderStatus(str, Enum):
    CREATED = "created"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class ReservationStatus(str, Enum):
    RESERVED = "reserved"
    FULFILLED = "fulfilled"
    RELEASED = "released"
from app.shared.exceptions.inventory_errors import InsufficientStock, InvalidRelease


class Stock:
    def __init__(self, total: int, available: int, reserved: int):
        self.total = total
        self.available = available
        self.reserved = reserved

    def increase(self, qty: int):
        self.total += qty
        self.available += qty

    def decrease(self, qty: int):
        if self.available < qty:
            raise InsufficientStock()
        self.total -= qty
        self.available -= qty

    def reserve(self, qty: int):
        if self.available < qty:
            raise InsufficientStock()
        self.available -= qty
        self.reserved += qty

    def release(self, qty: int):
        if self.reserved < qty:
            raise InvalidRelease()
        self.reserved -= qty
        self.available += qty

    def adjust(self, qty: int):
        self.total = qty
        self.available = qty
        self.reserved = 0
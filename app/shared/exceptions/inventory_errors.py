from app.shared.exceptions.core_errors import AppError


class InventoryError(AppError):
    pass

#database

class InventoryDBError(InventoryError):
    pass

# stock

class InsufficientStock(InventoryError):
    pass

class StockNotFound(InventoryError):
    pass

# reservations

class ReservationNotExists(InventoryError):
    pass

class ReservationInactive(InventoryError):
    pass


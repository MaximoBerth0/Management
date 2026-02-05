from app.shared.exceptions.core_errors import AppError


class InventoryError(AppError):
    pass

#database

class InventoryDBError(InventoryError):
    pass

# products

class ProductAlreadyExists(InventoryError):
    pass

class ProductNotFound(InventoryError):
    pass

class ProductAlreadyInactive(InventoryError):
    pass

class ProductSkuAlreadyExists(InventoryError):
    pass

# stock

class InsufficientStock(InventoryError):
    pass

class StockNotFound(InventoryError):
    pass

class InvalidRelease(InventoryError):
    pass

# reservations

class ReservationNotExists(InventoryError):
    pass

class ReservationInactive(InventoryError):
    pass


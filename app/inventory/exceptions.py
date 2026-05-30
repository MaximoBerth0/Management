from app.core.global_errors import AppError


class InventoryError(AppError):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "INVENTORY_ERROR",
    ):
        super().__init__(message, status_code, error_code)


class ProductNotFound(InventoryError):
    def __init__(self, message: str = "Product not found"):
        super().__init__(
            message=message,
            status_code=404,
            error_code="PRODUCT_NOT_FOUND",
        )

class ProductNameIsRequired(InventoryError):
    def __init__(self, message: str = "Product name is required"):
        super().__init__(
            message=message,
            status_code=400,
            error_code="PRODUCT_NAME_IS_REQUIRED",
        )

class SKUIsRequired(InventoryError):
    def __init__(self, message: str = "SKU is required"):
        super().__init__(
            message=message,
            status_code=400,
            error_code="SKU_IS_REQUIRED",
        )

class ProductAlreadyExits(InventoryError):
    def __init__(self, message: str = "Product already exists"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="PRODUCT_ALREADY_EXISTS",
        )

class CategoryAlreadyExists(InventoryError):
    def __init__(self, message: str = "Category already exists"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CATEGORY_ALREADY_EXISTS",
        )

class NoParametersProvide(InventoryError):
    def __init__(self, message: str = "At least one field is required"):
        super().__init__(
            message=message,
            status_code=400,
            error_code="NO_PARAMETERS_PROVIDE",
        )

class CategoryNotFound(InventoryError):
    def __init__(self, message: str = "Category not found"):
        super().__init__(
            message=message,
            status_code=404,
            error_code="CATEGORY_NOT_FOUND",
        )


class CategoryNameIsRequired(InventoryError):
    def __init__(self, message: str = "Category name is required"):
        super().__init__(
            message=message,
            status_code=400,
            error_code="CATEGORY_NAME_IS_REQUIRED",
        )

class CategoryDescriptionIsRequired(InventoryError):
    def __init__(self, message: str = "Category description is required"):
        super().__init__(
            message=message,
            status_code=400,
            error_code="CATEGORY_DESCRIPTION_IS_REQUIRED",
        )

class InvalidLocation(InventoryError):
    def __init__(self, message: str = "location id cannot be empty"):
        super().__init__(
            message=message,
            status_code=400,
            error_code="INVALID_LOCATION_ID",
        )

class InvalidQuantityStock(InventoryError):
    def __init__(self, message: str = "quantity must be > 0"):
        super().__init__(
            message=message,
            status_code=400,
            error_code="INVALID_QUANTITY_STOCK",
        )

class InvalidProductOrLocation(InventoryError):
    def __init__(self, message: str = "invalid product or location id"):
        super().__init__(
            message=message,
            status_code=400,
            error_code="INVALID_PRODUCT_OR_LOCATION",
        )

class StockNegative(InventoryError):
    def __init__(self, message: str = "stock cannot be negative"):
        super().__init__(
            message=message,
            status_code=400,
            error_code="STOCK_NEGATIVE",
        )

class StockNotFound(InventoryError):
    def __init__(self, message: str = "Stock not found"):
        super().__init__(
            message=message,
            status_code=404,
            error_code="STOCK_NOT_FOUND",
        )

class InsufficientStock(InventoryError):
    def __init__(self, message: str = "Insufficient available stock"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="INSUFFICIENT_STOCK",
        )

class ReservationNotFound(InventoryError):
    def __init__(self, message: str = "Reservation not found"):
        super().__init__(
            message=message,
            status_code=404,
            error_code="RESERVATION_NOT_FOUND",
        )

class InvalidReservationStatus(InventoryError):
    def __init__(self, message: str = "Reservation is not in a valid state"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="INVALID_RESERVATION_STATUS",
        )
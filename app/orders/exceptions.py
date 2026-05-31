from app.core.global_errors import AppError


class OrderError(AppError):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "ORDER_ERROR",
    ):
        super().__init__(message, status_code, error_code)


class OrderNotFound(OrderError):
    def __init__(self, message: str = "Order not found"):
        super().__init__(
            message=message,
            status_code=404,
            error_code="ORDER_NOT_FOUND",
        )

class OrderIsNotPending(OrderError):
    def __init__(self, message: str = "Order status should be pending"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="ORDER_IS_NOT_PENDING",
        )

        
from app.core.global_errors import AppError


class AuthError(AppError):
    def __init__(
        self,
        message: str,
        status_code: int = 401,
        error_code: str = "AUTH_ERROR",
    ):
        super().__init__(message, status_code, error_code)


class InvalidCredentials(AuthError):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="INVALID_CREDENTIALS",
        )


class TokenExpired(AuthError):
    def __init__(self, message: str = "Token has expired"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="TOKEN_EXPIRED",
        )


class TokenInvalid(AuthError):
    def __init__(self, message: str = "Token is invalid"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="TOKEN_INVALID",
        )

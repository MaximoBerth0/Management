from app.shared.exceptions.core_errors import AppError


class TokenError(AppError):
    pass


class TokenExpired(TokenError):
    pass


class TokenInvalid(TokenError):
    pass


class AuthError(AppError):
    pass


class InvalidCredentials(AuthError):
    pass

"""base application error"""


class AppError(Exception):
    """Base error for the application"""
    pass


"""token errors"""


class TokenError(AppError):
    pass


class TokenExpired(TokenError):
    pass


class TokenInvalid(TokenError):
    pass


"""authentication errors"""


class AuthError(AppError):
    pass


class InvalidCredentials(AuthError):
    pass


"""user errors"""


class UserError(AppError):
    pass


class UserNotFound(UserError):
    pass


class UserAlreadyExists(UserError):
    pass


class UserInactive(UserError):
    pass


"""authorization errors"""


class PermissionDenied(AppError):
    pass


"""database errors"""


class RepositoryError(AppError):
    pass


"""application errors"""


class AppError(Exception):
    pass


"""tokens errors"""


class InvalidToken(AppError):
    pass


class TokenExpired(AppError):
    pass


"""authentication errors"""


class AuthError(AppError):
    pass


class InvalidCredentials(AuthError):
    pass


class TokenExpired(AuthError):
    pass


class TokenInvalid(AuthError):
    pass


"""user errors"""


class UserNotFound(Exception):
    pass


class UserAlreadyExists(Exception):
    pass


class UserInactive(Exception):
    pass


class InvalidCredentials(Exception):
    pass


"""authorization errors"""


class PermissionDenied(AppError):
    pass


"""database errors"""


class RepositoryError(AppError):
    pass

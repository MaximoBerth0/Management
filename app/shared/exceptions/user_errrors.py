from app.shared.exceptions.core_errors import AppError


class UserError(AppError):
    pass


class UserNotFound(UserError):
    pass


class UserAlreadyExists(UserError):
    pass


class UserInactive(UserError):
    pass

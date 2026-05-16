class AppError(Exception):
    pass

class UserError(AppError):
    pass


class UserNotFound(UserError):
    pass


class UserAlreadyExists(UserError):
    pass


class UserInactive(UserError):
    pass

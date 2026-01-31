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


"""rbac and roles errors"""


class PermissionDenied(AppError):
    pass

class PermissionNotFound(Exception):
    pass

class PermissionAlreadyExists(Exception):
    pass

class RoleNotFound(Exception):
    pass

class RoleAlreadyExists(Exception):
    pass

class SystemRoleModificationError(Exception):
    pass

class PermissionAlreadyAssignedToRole(Exception):
    pass

class PermissionNotAssignedToRole(Exception):
    pass

class RolePermissionNotFound(Exception):
    pass

class RoleAlreadyAssignedToUser(Exception):
    pass

class RoleNotAssignedToUser(Exception):
    pass

class InvalidRole(Exception):
    pass

class InvalidPermissionOperation(Exception):
    pass

class UserRoleNotFound(Exception):
    pass


"""database errors"""

class RepositoryError(AppError):
    pass


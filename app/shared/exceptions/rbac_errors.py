from app.shared.exceptions.core_errors import AppError


# -------- Permissions --------

class PermissionError(AppError):
    """Base error for permission-related issues"""
    pass


class PermissionNotFound(PermissionError):
    pass


class PermissionDenied(PermissionError):
    pass


class PermissionAlreadyExists(PermissionError):
    pass


class PermissionAlreadyAssigned(PermissionError):
    pass


class PermissionNotAssigned(PermissionError):
    pass


class RolePermissionNotFound(PermissionError):
    pass


class RoleError(AppError):
    """Base error for role-related issues"""
    pass


class UserRoleNotFound(RoleError):
    pass


class RoleNotFound(RoleError):
    pass


class InvalidRole(RoleError):
    pass


class RoleAlreadyExists(RoleError):
    pass


class SystemRoleModificationError(RoleError):
    pass


class RoleAlreadyAssignedToUser(RoleError):
    pass



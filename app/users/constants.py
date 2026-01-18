from enum import Enum

class UserRole(str, Enum):
    CLIENT = "client"
    DRIVER = "driver"
    EMPLOYEE = "employee"
    ADMIN = "admin"

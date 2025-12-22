from enum import Enum


class Roles(str, Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"
    CLIENT = "client"
    DRIVER = "driver"

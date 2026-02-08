from app.core.constants.inventory_permissions import INVENTORY_PERMISSIONS
from app.core.constants.system_permissions import SYSTEM_PERMISSIONS
from app.core.constants.user_permissions import USER_PERMISSIONS

SYSTEM_ROLES = {
    "admin": SYSTEM_PERMISSIONS + INVENTORY_PERMISSIONS + USER_PERMISSIONS,

    "employee": [
        "products:view",
        "stock:in",
        "stock:out",
        "reservations:view",
    ],

    "driver": [
        "products:view",
        "reservations:view",
    ],

    "client": [
        "products:view",
        "reservations:view",  # own reserve
    ],
}
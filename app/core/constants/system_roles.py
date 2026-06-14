from app.core.constants.inventory_permissions import INVENTORY_PERMISSIONS
from app.core.constants.order_permissions import ORDER_PERMISSIONS
from app.core.constants.system_permissions import SYSTEM_PERMISSIONS
from app.core.constants.user_permissions import USER_PERMISSIONS

SYSTEM_ROLES = {
    "admin": SYSTEM_PERMISSIONS
    + INVENTORY_PERMISSIONS
    + USER_PERMISSIONS
    + ORDER_PERMISSIONS,
    "employee": [
        "product:view",
        "product:create",
        "product:update",
        "category:create",
        "category:remove",
        "stock:in",
        "stock:out",
        "stock:adjust",
        "stock:view",
        "location:list",
        "location:view",
        "order:create",
        "order:remove",
        "order:confirm",
        "order:cancel",
        "order:complete",
    ],
    "client": [],
}

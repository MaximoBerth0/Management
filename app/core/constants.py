SYSTEM_PERMISSIONS = [
    # roles
    "roles:view",
    "roles:create",
    "roles:update",
    "roles:delete",

    # role-permission
    "roles:rbac:view",
    "roles:rbac:update",

    # user-role
    "users:roles:view",
    "users:roles:update",
]

INVENTORY_PERMISSIONS = [
    "products:view",
    "products:create",
    "products:update",
    "products:deactivate",

    "stock:in",
    "stock:out",
    "stock:reserve",
    "stock:release",
    "stock:adjust",

    "reservations:view",
    "reservations:create",
    "reservations:update",
    "reservations:cancel",
]

SYSTEM_ROLES = {
    "admin": SYSTEM_PERMISSIONS + INVENTORY_PERMISSIONS,

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
        "reservations:view",  #own reserve
    ],
}
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

SYSTEM_ROLES = {
    "admin": list(SYSTEM_PERMISSIONS),
    "employee": [
        "users:roles:view",
    ],
    "driver": [
        "users:roles:view",
    ],
    "client": [],
}

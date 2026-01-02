SYSTEM_PERMISSIONS = [
    # roles
    "roles:view",
    "roles:create",
    "roles:update",
    "roles:delete",

    # role-permission
    "roles:permissions:view",
    "roles:permissions:update",

    # user-role
    "users:roles:view",
    "users:roles:update",
]

SYSTEM_ROLES = {
    "admin": SYSTEM_PERMISSIONS,
    "employee": [
        "users:roles:view",
    ],
    "driver": [
        "users:roles:view",
    ],
    "client": [],
}

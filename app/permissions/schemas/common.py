from pydantic import BaseModel

from app.permissions.schemas.permission import PermissionRead
from app.permissions.schemas.role import RoleRead


class PermissionsOverview(BaseModel):
    roles: list[RoleRead]
    permissions: list[PermissionRead]

class Message(BaseModel):
    detail: str

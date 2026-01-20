from pydantic import BaseModel

from app.rbac.schemas.permission import PermissionRead
from app.rbac.schemas.role import RoleRead


class PermissionsOverview(BaseModel):
    roles: list[RoleRead]
    permissions: list[PermissionRead]

class Message(BaseModel):
    detail: str

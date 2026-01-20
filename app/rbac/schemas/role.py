from pydantic import BaseModel

from app.rbac.schemas.permission import PermissionRead


class RoleRead(BaseModel):
    id: int
    name: str
    permissions: list[PermissionRead]

class RoleCreate(BaseModel):
    name: str
    permissions: list[int] = []

class RoleUpdate(BaseModel):
    name: str | None = None
    permissions: list[int] | None = None

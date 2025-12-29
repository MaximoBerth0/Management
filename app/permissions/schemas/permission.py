from pydantic import BaseModel


class PermissionRead(BaseModel):
    id: int
    name: str

class PermissionCreate(BaseModel):
    name: str  
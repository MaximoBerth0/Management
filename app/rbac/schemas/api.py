from pydantic import BaseModel, Field
from typing import Optional, List


# role request

class RoleCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


class RoleUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


# permission request

class AddPermissionToRoleRequest(BaseModel):
    permission_id: int


class RemovePermissionFromRoleRequest(BaseModel):
    permission_id: int



# response model

class PermissionResponse(BaseModel):
    id: int
    name: str


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    permissions: List[PermissionResponse] = []


class UserRoleResponse(BaseModel):
    user_id: int
    role_id: int

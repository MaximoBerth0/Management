from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

# request


class RoleCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


class RoleUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


class AddPermissionToRoleRequest(BaseModel):
    permission_id: int


class RemovePermissionFromRoleRequest(BaseModel):
    permission_id: int


# response

class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    permissions: List[PermissionResponse] = []


class UserRoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    role_id: int

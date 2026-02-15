from pydantic import BaseModel, Field
from typing import Optional


#input

class RoleCreateDTO(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class RoleUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class AssignRoleToUserDTO(BaseModel):
    user_id: int
    role_id: int


class RemoveRoleFromUserDTO(BaseModel):
    user_id: int
    role_id: int


class AddPermissionToRoleDTO(BaseModel):
    permission_id: int


class RemovePermissionFromRoleDTO(BaseModel):
    permission_id: int


#output

class RoleResponseDTO(BaseModel):
    id: int
    name: str
    description: Optional[str]

    model_config = {
        "from_attributes": True  # allows ORM → DTO
    }



from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreateRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=8)


class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(default=None, min_length=3, max_length=150)


class UserStatusUpdateRequest(BaseModel):
    is_active: bool


class UserReadResponse(ORMModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    is_superuser: bool
    created_at: datetime


class UserListItemResponse(ORMModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    is_superuser: bool
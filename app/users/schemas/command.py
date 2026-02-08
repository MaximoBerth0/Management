from pydantic import BaseModel, EmailStr
from typing import Optional


class CreateUserCommand(BaseModel):
    email: EmailStr
    username: str
    password: str


class UpdateUserCommand(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None

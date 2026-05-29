from typing import Optional

from pydantic import BaseModel, EmailStr


class CreateUserCommand(BaseModel):
    email: EmailStr
    username: str
    hashed_password: str


class UpdateUserCommand(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None

from typing import Literal

from pydantic import BaseModel, EmailStr, Field


# input

class LoginDTO(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=50)


class LogoutDTO(BaseModel):
    refresh_token: str


class RefreshSessionDTO(BaseModel):
    refresh_token: str


class ForgotPasswordDTO(BaseModel):
    email: EmailStr


class ResetPasswordDTO(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=50)


class ChangePasswordDTO(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=50)


# output

class TokenResponseDTO(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"

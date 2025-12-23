from fastapi import APIRouter, Depends, status

from app.auth.container import get_auth_service
from app.auth.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.auth.service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

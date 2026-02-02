from fastapi import APIRouter, Depends, status

from app.auth.service import AuthService
from app.users.models import User
from app.auth.dependencies import get_auth_service, get_current_user
from app.auth.schemas import (
    LoginRequest,
    TokenResponse,
    LogoutRequest,
    RefreshTokensRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    return await service.login(
        email=str(data.email),
        password=data.password,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    data: RefreshTokensRequest,
    service: AuthService = Depends(get_auth_service),
):
    return await service.refresh_session(
        refresh_token=data.refresh_token,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: LogoutRequest,
    service: AuthService = Depends(get_auth_service),
):
    await service.logout(
        refresh_token=data.refresh_token,
    )


@router.post("/forgot", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(
    data: ForgotPasswordRequest,
    service: AuthService = Depends(get_auth_service),
):
    await service.forgot_password(
        email=str(data.email),
    )


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    data: ResetPasswordRequest,
    service: AuthService = Depends(get_auth_service),
):
    await service.reset_password(
        token=data.token,
        new_password=data.new_password,
    )


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    await service.change_password(
        current_user=current_user,
        old_password=data.old_password,
        new_password=data.new_password,
    )

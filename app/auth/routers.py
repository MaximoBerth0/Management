from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_auth_service, get_current_user
from app.auth.schemas.api import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshTokensRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.auth.schemas.dto import (
    ChangePasswordDTO,
    ForgotPasswordDTO,
    LoginDTO,
    LogoutDTO,
    RefreshSessionDTO,
    ResetPasswordDTO,
)
from app.auth.service import AuthService
from app.users.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    return await service.login(LoginDTO(email=data.email, password=data.password))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    data: RefreshTokensRequest,
    service: AuthService = Depends(get_auth_service),
):
    return await service.refresh_session(
        RefreshSessionDTO(refresh_token=data.refresh_token)
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: LogoutRequest,
    service: AuthService = Depends(get_auth_service),
):
    await service.logout(LogoutDTO(refresh_token=data.refresh_token))


@router.post("/forgot", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(
    data: ForgotPasswordRequest,
    service: AuthService = Depends(get_auth_service),
):
    await service.forgot_password(ForgotPasswordDTO(email=data.email))


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    data: ResetPasswordRequest,
    service: AuthService = Depends(get_auth_service),
):
    await service.reset_password(
        ResetPasswordDTO(token=data.token, new_password=data.new_password)
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
        current_user,
        ChangePasswordDTO(
            old_password=data.old_password, new_password=data.new_password
        ),
    )

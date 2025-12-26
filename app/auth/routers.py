from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, status

from app.auth.container import get_auth_service
from app.auth.dependencies import get_current_user
from app.auth.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokensRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.auth.service import AuthService
from app.users.models import User

if TYPE_CHECKING:
    from app.users.models import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    access_token, refresh_token = service.login(
        email=data.email,
        password=data.password,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
def logout(
    refresh_token: RefreshTokensRequest,
    service: AuthService = Depends(get_auth_service),
):
    service.logout(refresh_token=refresh_token.refresh_token)

@router.post(
    "/refresh-token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def refresh_token(
    data: RefreshTokensRequest,
    service: AuthService = Depends(get_auth_service),
):
    access_token, new_refresh_token = service.refresh_token(
        refresh_token=data.refresh_token
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )

@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def change_password(
    data: ChangePasswordRequest,
    service: AuthService = Depends(get_auth_service),
    current_user: "User" = Depends(get_current_user),
):
    service.change_password(
        user_id=current_user.id,
        old_password=data.old_password,
        new_password=data.new_password,
    )

@router.post(
    "/forgot-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def forgot_password(
    data: ForgotPasswordRequest,
    service: AuthService = Depends(get_auth_service),
):
    service.forgot_password(email=data.email)

@router.post(
    "/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
def reset_password(
    data: ResetPasswordRequest,
    service: AuthService = Depends(get_auth_service),
):
    service.reset_password(
        token=data.token,
        new_password=data.new_password,
    )


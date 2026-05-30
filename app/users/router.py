from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.rbac.dependencies import require_permission
from app.users.dependencies import provide_user_service
from app.users.model import User
from app.users.schemas import (
    DisableUserRequest,
    UserCreateRequest,
    UserListItemResponse,
    UserReadResponse,
    UserUpdateRequest,
)
from app.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register",
    response_model=UserReadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    data: UserCreateRequest,
    service: UserService = Depends(provide_user_service),
):
    return await service.register_user(
        email=data.email,
        username=data.username,
        password=data.password,
    )


@router.put(
    "/me",
    response_model=UserReadResponse,
)
async def update_profile(
    data: UserUpdateRequest,
    service: UserService = Depends(provide_user_service),
    current_user: User = Depends(get_current_user),
):
    return await service.update_profile(
        current_user=current_user,
        data=data.model_dump(exclude_unset=True),  # only include fields sent in the request
    )


@router.get(
    "/list",
    response_model=list[UserListItemResponse],
    dependencies=[Depends(require_permission("users:view"))],
)
async def list_users(
    service: UserService = Depends(provide_user_service),
):
    return await service.list_users()


@router.get(
    "/{user_id}",
    response_model=UserReadResponse,
    dependencies=[Depends(require_permission("users:view"))],
)
async def get_user_by_id(
    user_id: int,
    service: UserService = Depends(provide_user_service),
):
    return await service.get_user_by_id(user_id=user_id)


@router.get(
    "/email/{email}",
    response_model=UserReadResponse,
    dependencies=[Depends(require_permission("users:view"))],
)
async def get_user_by_email(
    email: str,
    service: UserService = Depends(provide_user_service),
):
    return await service.get_user_by_email(email=email)


@router.patch(
    "/{user_id}/disable-account",
    response_model=UserReadResponse,
    dependencies=[Depends(require_permission("users:disable"))],
)
async def disable_user(
    user_id: int,
    data: DisableUserRequest,
    service: UserService = Depends(provide_user_service),
    current_user: User = Depends(get_current_user),
):
    return await service.disable_account(
        user_id=user_id,
        disabled_by_user_id=current_user.id,
        reason=data.reason,
    )


@router.patch(
    "/{user_id}/enable",
    response_model=UserReadResponse,
    dependencies=[Depends(require_permission("users:enable"))],
)
async def enable_user(
    user_id: int,
    service: UserService = Depends(provide_user_service),
):
    return await service.enable_account(user_id=user_id)

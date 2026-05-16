from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.rbac.dependencies import require_permission
from app.users.dependencies import get_user_service
from app.users.models import User
from app.users.service import UserService

from app.users.schemas.api import (
    UserCreateRequest,
    UserUpdateRequest,
    UserReadResponse,
    UserListItemResponse,
    DisableUserRequest,
)

from app.users.schemas.command import (
    CreateUserCommand,
    UpdateUserCommand,
)

router = APIRouter(prefix="/users", tags=["Users"])

@router.post(
    "/register",
    response_model=UserReadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    data: UserCreateRequest,
    service: UserService = Depends(get_user_service),
):
    command = CreateUserCommand(
        email=data.email,
        username=data.username,
        hashed_password=data.password,
    )

    return await service.register_user(command)

@router.put(
    "/me",
    response_model=UserReadResponse,
)
async def update_profile(
    data: UserUpdateRequest,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    command = UpdateUserCommand(
        email=data.email,
        username=data.username,
    )

    return await service.update_profile(
        current_user=current_user,
        data=command,
    )

@router.get(
    "/list",
    response_model=list[UserListItemResponse],
    dependencies=[Depends(require_permission("users:view"))],
)
async def list_users(
    service: UserService = Depends(get_user_service),
):
    return await service.list_users()


@router.get(
    "/{user_id}",
    response_model=UserReadResponse,
    dependencies=[Depends(require_permission("users:view"))],
)
async def get_user_by_id(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    return await service.get_user_by_id(user_id=user_id)


@router.get(
    "/email/{email}",
    response_model=UserReadResponse,
    dependencies=[Depends(require_permission("users:view"))],
)
async def get_user_by_email(
    email: str,
    service: UserService = Depends(get_user_service),
):
    return await service.get_user_by_email(email=email)


@router.patch(
    "/{user_id}/disable-account",
    response_model=UserReadResponse,
    dependencies=[Depends(require_permission("users:update"))],
)
async def disable_user(
    user_id: int,
    data: DisableUserRequest,
    service: UserService = Depends(get_user_service),
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
    dependencies=[Depends(require_permission("users:update"))],
)
async def enable_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    return await service.enable_account(user_id=user_id)

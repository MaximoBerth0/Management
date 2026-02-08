from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.rbac.dependencies import require_permission
from app.users.dependencies import get_user_service
from app.users.models import User
from app.users.service import UserService

from app.users.schemas.https import (
    UserCreateRequest,
    UserUpdateRequest,
    UserReadResponse,
    UserListItemResponse,
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
        password=data.password,
    )

    return await service.register_user(command)


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
    "/me",
    response_model=UserReadResponse,
)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user

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
    "/{user_id}",
    response_model=UserReadResponse,
    dependencies=[Depends(require_permission("users:view"))],
)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    return await service.get_user(user_id=user_id)


@router.patch(
    "/{user_id}/disable",
    response_model=UserReadResponse,
    dependencies=[Depends(require_permission("users:update"))],
)
async def disable_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    return await service.set_user_active(
        current_user=current_user,
        user_id=user_id,
        active=False,
    )


@router.patch(
    "/{user_id}/enable",
    response_model=UserReadResponse,
    dependencies=[Depends(require_permission("users:update"))],
)
async def enable_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    return await service.set_user_active(
        current_user=current_user,
        user_id=user_id,
        active=True,
    )

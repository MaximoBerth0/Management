from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.users.dependencies import get_user_service
from app.users.models import User
from app.users.schemas import UserCreate, UserRead, UserUpdate
from app.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    return await service.register_user(
        data=data,
        role=data.role,
    )

@router.get("/list", response_model=list[UserRead])
async def list_users(
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    return await service.list_users(
        current_user=current_user,
    )

@router.get("/me", response_model=UserRead)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user

@router.put("/me", response_model=UserRead)
async def update_profile(
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    return await service.update_profile(
        current_user=current_user,
        data=data,
    )

@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_user(
        current_user=current_user,
        user_id=user_id,
    )

@router.patch("/{user_id}/disable", response_model=UserRead)
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

@router.patch("/{user_id}/enable", response_model=UserRead)
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

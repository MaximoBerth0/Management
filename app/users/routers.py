from fastapi import APIRouter, Depends, status

from app.auth.dependencies import get_current_user
from app.permissions.dependencies import require_permission
from app.users.dependencies import get_user_service
from app.users.models import User
from app.users.schemas import UserCreate, UserOut, UserUpdate
from app.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/create", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    return service.create_user(data)

@router.get("/list")
def list_users(
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission("users:view")),
):
    return service.list_users()

@router.get("/profile", response_model=UserOut)
def get_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user

@router.put("/profile/update")
def update_profile(
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
):
    return service.update_user(current_user.id, data)

@router.delete("/{user_id}/delete")
def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission("users:delete")),
):
    return service.delete_user(user_id)

@router.delete("/{user_id}/delete")
def disable_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission("users:disable")),
):
    return service.disable_user(user_id)

@router.delete("/{user_id}/delete")
def enable_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_permission("users:enable")),
):
    return service.enable_user(user_id)

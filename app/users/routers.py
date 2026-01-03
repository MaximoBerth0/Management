from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.permissions.dependencies import require_permission
from app.users import schemas, service
from app.users.models import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/create", status_code=status.HTTP_201_CREATED)  # anyone
def create_user(
    data: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    return service.create_user(db, data)


@router.get("/list")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:view")),
):
    return service.list_users(db)


@router.get("/profile", response_model=schemas.UserOut)
def get_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user



@router.put("/profile/update")
def update_profile(
    data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.update_user(db, current_user.id, data)

@router.delete("/{user_id}/delete")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:delete")),
):
    return service.delete_user(db, user_id)


@router.post("/{user_id}/disable")
def disable_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:update")),
):
    return service.disable_user(db, user_id)


@router.post("/{user_id}/enable")
def enable_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:update")),
):
    return service.enable_user(db, user_id)


@router.get("/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:view")),
):
    return service.get_user_by_id(db, user_id)


@router.put("/{user_id}/update")
def update_user(
    user_id: int,
    data: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("users:update")),
):
    return service.update_user(db, user_id, data)

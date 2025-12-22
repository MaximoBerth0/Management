from app.auth.dependencies import get_current_user
from app.users.models import User
from fastapi import Depends, HTTPException, status


def require_roles(allowed_roles: list[str]):
    def dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="inactive user"
            )
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="not enought permissions"
            )
        return current_user

    return dependency

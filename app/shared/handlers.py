from app.shared.exceptions import UserAlreadyExists
from fastapi import Request
from fastapi.responses import JSONResponse


def user_already_exists_handler(request: Request, exc: UserAlreadyExists):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )


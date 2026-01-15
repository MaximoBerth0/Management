from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.session import init_db

from app.auth.routers import router as auth_router
from app.users.routers import router as users_router
from app.permissions.routers import router as permissions_router

from app.shared.exceptions import UserAlreadyExists
from app.shared.handlers import user_already_exists_handler


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield
    # place for future shutdown logic (close redis, etc.)


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Exception handlers
app.add_exception_handler(
    UserAlreadyExists,
    user_already_exists_handler,
)

# Routers
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(permissions_router, prefix="/permissions", tags=["permissions"])

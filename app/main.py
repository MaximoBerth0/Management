from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.session import init_db

from app.auth.routers import router as auth_router
from app.users.routers import router as users_router
from app.rbac.routers import router as rbac_router

from app.shared.exceptions.core_errors import AppError


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

# Exception handler
@app.exception_handler(AppError)
async def app_error_handler(request, exc: AppError):
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.__class__.__name__,
            "detail": str(exc),
        },
    )

# Routers
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(rbac_router)

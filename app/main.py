import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth.routers import router as auth_router
from app.core.config import settings
from app.core.global_errors import AppError
from app.inventory.router import router as inventory_router
from app.observability.logging import setup_logging
from app.orders.router import router as order_router
from app.rbac.routers import router as rbac_router
from app.users.router import router as users_router

setup_logging()
logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.APP_NAME,
    docs_url=None if settings.ENV == "prod" else "/docs",
    redoc_url=None if settings.ENV == "prod" else "/redoc",
    openapi_url=None if settings.ENV == "prod" else "/openapi.json",
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
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "detail": exc.message}
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error_code": "INTERNAL_ERROR", "detail": "An unexpected error occurred"}
    )

# Routers
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(rbac_router)
app.include_router(inventory_router)
app.include_router(order_router)
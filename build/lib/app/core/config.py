from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):

    # App
    APP_NAME: str = "Management"
    ENV: str = "local"  # local | staging | production
    DEBUG: bool = False

    # Database (Async SQLAlchemy)
    DATABASE_URL: str

    # Security /Auth
    JWT_ALGORITHM: str = "RS256"
    JWT_PRIVATE_KEY: str
    JWT_PUBLIC_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_HASH_SCHEME: str = "argon2"

    # CORS
    CORS_ALLOW_ORIGINS: List[str] = []
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Redis/ Celery
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Observability
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: str | None = None
    PROMETHEUS_ENABLED: bool = True

    # Server
    UVICORN_WORKERS: int = 1
    GUNICORN_WORKERS: int = 2

    model_config = SettingsConfigDict(
        env_file=".env.example",
        case_sensitive=True,
    )


settings = Settings()


from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Management"
    ENV: str = "prod"
    DEBUG: bool = False

    # Database (Postgres)
    DATABASE_URL: str

    # Connection pool
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True
    DB_ECHO: bool = False

    # Connection Timeouts
    DB_CONNECT_TIMEOUT: int = 10
    DB_COMMAND_TIMEOUT: int = 60
    DB_STATEMENT_TIMEOUT: int = 30000

    # Security / Auth
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_HASH_SCHEME: str = "argon2"

    # Server
    UVICORN_WORKERS: int = 1
    GUNICORN_WORKERS: int = 4

    # CORS
    CORS_ALLOW_ORIGINS: list[str]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    CORS_ALLOW_HEADERS: list[str] = ["Authorization", "Content-Type"]

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=None,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_prod_settings(self) -> "Settings":
        if self.ENV == "prod":
            assert self.CORS_ALLOW_ORIGINS != ["*"], \
                "Wildcard CORS origins are not allowed in prod"
            assert len(self.SECRET_KEY) >= 32, \
                "SECRET_KEY must be at least 32 characters in prod"
            assert not self.DEBUG, \
                "DEBUG must be False in prod"
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings() # type:ignore


settings = get_settings()
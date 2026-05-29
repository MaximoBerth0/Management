from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Management"
    ENV: str = "local"  # local | staging | prod
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

    # Connection Timeouts (asyncpg specific)
    DB_CONNECT_TIMEOUT: int = 10  # Timeout to establish connection
    DB_COMMAND_TIMEOUT: int = 60  # Timeout for individual queries
    DB_STATEMENT_TIMEOUT: int = 30000  # PostgreSQL statement timeout (ms)

    # Security /Auth
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_HASH_SCHEME: str = "argon2"  # > security/passwords.py

    # Server
    UVICORN_WORKERS: int = 1
    GUNICORN_WORKERS: int = 2

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()  # type: ignore

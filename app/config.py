from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Management"
    # Database
    DATABASE_URL: str
    # Security
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"

settings = Settings()



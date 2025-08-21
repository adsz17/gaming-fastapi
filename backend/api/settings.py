from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    ENV: str = "production"
    JWT_SECRET: str = "changeme"  # se sobreescribe por env
    JWT_EXPIRES_MIN: int = 60
    DATABASE_URL: str = ""
    CORS_ORIGINS: List[AnyHttpUrl] = []

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

from pydantic_settings import BaseSettings
from typing import ClassVar
import os


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv('DATABASE_URL')
    REFRESH_SECRET_KEY: str = os.getenv('REFRESH_SECRET_KEY')
    REFRESH_TOKEN_EXPIRE_DAYS: int = os.getenv('REFRESH_TOKEN_EXPIRE_DAYS')
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = 'HS256'
    UPLOAD_DIR: str = os.getenv('UPLOAD_DIR')
    ALLOWED_EXTENSIONS: ClassVar[set] = {
        'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'
    }


settings = Settings()

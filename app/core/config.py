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
    TEMP_DIR: str = os.getenv('TEMP_DIR')
    ALLOWED_EXTENSIONS: ClassVar[set] = {
        'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'
    }
    MAIL_USERNAME: str = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD: str = os.getenv('MAIL_PASSWORD')
    MAIL_FROM: str = os.getenv('MAIL_FROM')
    MAIL_PORT: int = os.getenv('MAIL_PORT')
    MAIL_SERVER: str = os.getenv('MAIL_SERVER')
    MAIL_STARTTLS: bool = os.getenv('MAIL_STARTTLS')
    MAIL_SSL_TLS: bool = os.getenv('MAIL_SSL_TLS')
    FRONTEND_URL: str = os.getenv('FRONTEND_URL')


settings = Settings()

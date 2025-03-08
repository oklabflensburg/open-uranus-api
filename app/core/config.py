from pydantic_settings import BaseSettings

import os



class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv('DATABASE_URL')
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = 'HS256'



settings = Settings()

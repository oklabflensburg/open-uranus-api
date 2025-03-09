from sqlmodel import SQLModel, Field
from pydantic import BaseModel, validator
from typing import Optional

from app.models.user import UserBase
from app.services.auth import validate_password



class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    i18n_locale_id: Optional[int] = None

    @validator('password')
    def validate_user_password(cls, password):
        return validate_password(password)

    class Config:
        from_attributes = True



class UserCreate(UserBase):
    password: str

    @validator('password')
    def validate_user_password(cls, password):
        return validate_password(password)


class UserRead(UserBase):
    id: int



class UserSignin(BaseModel):
    username: str
    password: str



class Token(BaseModel):
    access_token: str
    token_type: str
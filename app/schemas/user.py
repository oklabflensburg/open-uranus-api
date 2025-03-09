from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from typing import Optional

from app.models.user import UserBase



class UserCreate(UserBase):
    password: str



class UserRead(UserBase):
    id: int



class UserLogin(BaseModel):
    username: str
    password: str



class Token(BaseModel):
    access_token: str
    token_type: str
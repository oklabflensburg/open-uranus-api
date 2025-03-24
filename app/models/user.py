from sqlmodel import SQLModel, Field
from datetime import datetime
from pydantic import EmailStr
from typing import Optional


class UserBase(SQLModel):
    email_address: EmailStr
    password_hash: str
    disabled: bool = False


class User(UserBase, table=True):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'uranus'}

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None

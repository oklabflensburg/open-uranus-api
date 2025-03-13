from sqlmodel import SQLModel, Field
from datetime import datetime
from pydantic import EmailStr
from typing import Optional



class UserBase(SQLModel):
    first_name: str
    last_name: str
    email_address: EmailStr
    username: str
    disabled: bool = False
    i18n_locale_id: int



class User(UserBase, table=True):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'uranus'}

    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None
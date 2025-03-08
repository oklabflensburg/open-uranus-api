from sqlmodel import SQLModel, Field
from typing import Optional

from app.models.user import UserBase



# Used for creating a user, excluding the ID
class UserCreate(UserBase):
    pass



# Read-only representation with ID
class UserRead(UserBase):
    id: int



class UserUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email_address: Optional[str] = None
    username: Optional[str] = None
    password_hash: Optional[str] = None
    disabled: Optional[bool] = None
    i18n_locale_id: Optional[int] = None
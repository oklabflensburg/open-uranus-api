from sqlmodel import SQLModel, Field
from typing import Optional



class UserBase(SQLModel):
    first_name: str
    last_name: str
    email_address: str
    username: str
    password_hash: str
    disabled: bool = False
    i18n_locale_id: int



class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)



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
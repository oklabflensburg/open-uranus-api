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
from sqlmodel import SQLModel, Field
from typing import Optional



class LicenseType(SQLModel, table=True):
    __tablename__ = 'license_type'
    __table_args__ = {'schema': 'uranus'}

    id: int = Field(primary_key=True)
    name: str = Field(max_length=255)
    short_name: str = Field(max_length=255)
    url: str = Field(max_length=255)
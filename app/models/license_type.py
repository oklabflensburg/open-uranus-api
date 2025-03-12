from sqlmodel import SQLModel, Field
from typing import Optional



class LicenseTypeBase(SQLModel):
    i18n_locale_id: int = Field(foreign_key='uranus.i18n_locale.id', nullable=False)
    name: str = Field(max_length=255)
    short_name: str = Field(max_length=255)
    url: str = Field(max_length=255)



class LicenseType(LicenseTypeBase, table=True):
    __tablename__ = 'license_type'
    __table_args__ = {'schema': 'uranus'}

    id: Optional[int] = Field(default=None, primary_key=True)
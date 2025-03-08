from sqlmodel import SQLModel, Field
from typing import Optional



class ImageType(SQLModel, table=True):
    __tablename__ = 'image_type'
    __table_args__ = {'schema': 'uranus'}

    id: int = Field(primary_key=True)
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)
    i18n_locale_id: int = Field(foreign_key='uranus.i18n_locale.id')
    type_id: int
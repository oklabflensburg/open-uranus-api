from sqlmodel import SQLModel, Field
from typing import Optional



class ImageTypeBase(SQLModel):
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)
    i18n_locale_id: int = Field(foreign_key='uranus.i18n_locale.id')
    type_id: int



class ImageType(ImageTypeBase, table=True):
    __tablename__ = 'image_type'
    __table_args__ = {'schema': 'uranus'}

    id: Optional[int] = Field(default=None, primary_key=True)
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone



class ImageBase(SQLModel):
    origin_name: str = Field(max_length=255)
    mime_type: str = Field(max_length=255)
    license_type_id: Optional[int] = Field(foreign_key='uranus.license_type.id')
    created_by: Optional[str] = Field(default=None, max_length=255)
    copyright: Optional[str] = Field(default=None, max_length=255)
    image_type_id: Optional[int] = Field(foreign_key='uranus.image_type.id')
    alt_text: Optional[str] = None
    caption: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    source_name: str = Field(max_length=64, unique=True)



class Image(ImageBase, table=True):
    __tablename__ = 'image'
    __table_args__ = {'schema': 'uranus'}

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None
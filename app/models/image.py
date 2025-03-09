from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime



class ImageBase(SQLModel):
    origin_name: str = Field(max_length=255)
    mime_type: str = Field(max_length=255)
    license_type_id: int = Field(foreign_key='uranus.license_type.id')
    created_by: Optional[str] = Field(default=None, max_length=255)
    copyright: Optional[str] = Field(default=None, max_length=255)
    image_type_id: int = Field(foreign_key='uranus.image_type.id')
    alt_text: Optional[str] = None
    caption: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = None
    source_name: str = Field(max_length=64, unique=True)



class Image(ImageBase, table=True):
    __tablename__ = 'image'
    __table_args__ = {'schema': 'uranus'}

    id: Optional[int] = Field(default=None, primary_key=True)
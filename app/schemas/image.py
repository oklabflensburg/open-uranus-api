from pydantic import BaseModel
from typing import Optional



class ImageCreate(BaseModel):
    image_origin_name: str
    image_type_id: Optional[int] = None
    image_license_type_id: Optional[int] = None
    image_source_name: str
    image_alt_text: Optional[int] = None
    image_caption: Optional[int] = None
    image_copyright: Optional[str] = None
    image_mime_type: str
    image_width: int
    image_height: int
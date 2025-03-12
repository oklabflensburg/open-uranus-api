from pydantic import BaseModel



class ImageTypeResponse(BaseModel):
    image_type_id: int
    image_type_name: str
    image_locale_id: int

from pydantic import BaseModel



class SpaceTypeResponse(BaseModel):
    space_type_id: int
    space_type_name: str

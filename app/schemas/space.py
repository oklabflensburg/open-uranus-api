from pydantic import BaseModel
from typing import Optional



class SpaceCreate(BaseModel):
    space_venue_id: int
    space_name: str
    space_total_capacity: Optional[int] = None
    space_seating_capacity: Optional[int] = None
    space_type_id: Optional[int] = None
    space_building_level: Optional[int] = None
    space_url: Optional[str] = None



class SpaceResponse(SpaceCreate):
    space_id: int
from pydantic import BaseModel



class VenueTypeResponse(BaseModel):
    venue_type_id: int
    venue_type_name: str

from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime, date



class VenueGeoJSONPoint(BaseModel):
    type: Literal['Point']
    coordinates: List[float]



class VenueResponse(BaseModel):
    id: int 
    organizer_id: Optional[int] = None
    name: str 
    street: Optional[str] = None
    house_number: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    country_code: Optional[str] = None
    created_at: datetime
    modified_at: Optional[datetime] = None
    county_code: Optional[str] = None
    opened_at: Optional[date] = None
    closed_at: Optional[date] = None
    geojson: Optional[VenueGeoJSONPoint] = None

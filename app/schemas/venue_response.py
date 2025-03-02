from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime, date



class VenueGeoJSONPoint(BaseModel):
    type: Literal['Point']
    coordinates: List[float]



class VenueResponse(BaseModel):
    venue_id: int
    organizer_name: Optional[str] = None
    organizer_url: Optional[str] = None
    venue_name: str
    street: Optional[str] = None
    house_number: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    country_code: Optional[str] = None
    opened_at: Optional[date] = None
    closed_at: Optional[date] = None
    geojson: Optional[VenueGeoJSONPoint] = None

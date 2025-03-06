from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime, date



class VenueGeoJSONPoint(BaseModel):
    type: Literal['Point']
    coordinates: List[float]



class VenueResponse(BaseModel):
    venue_id: int
    venue_name: str
    venue_type: Optional[str] = None
    venue_street: Optional[str] = None
    venue_house_number: Optional[str] = None
    venue_postal_code: Optional[str] = None
    venue_city: Optional[str] = None
    opened_at: Optional[date] = None
    closed_at: Optional[date] = None
    organizer_name: Optional[str] = None
    organizer_url: Optional[str] = None
    geojson: Optional[VenueGeoJSONPoint] = None

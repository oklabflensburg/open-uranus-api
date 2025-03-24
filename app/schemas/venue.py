from pydantic import BaseModel
from typing import Optional, List
from datetime import date

from app.models.venue import VenueBase


class VenueCreate(BaseModel):
    venue_name: str
    venue_organizer_id: Optional[int] = None
    venue_type_ids: Optional[List[int]] = None
    venue_street: Optional[str] = None
    venue_house_number: Optional[str] = None
    venue_postal_code: Optional[str] = None
    venue_city: Optional[str] = None
    venue_country_code: Optional[str] = None
    venue_state_code: Optional[str] = None
    venue_opened_at: Optional[date] = None
    venue_closed_at: Optional[date] = None
    venue_latitude: float
    venue_longitude: float


class VenueRead(VenueBase):
    id: int

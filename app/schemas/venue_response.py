from pydantic import BaseModel, field_validator
from typing import Optional, List, Literal
from datetime import date

from app.services.validators import validate_positive_int32


class VenueGeoJSONPoint(BaseModel):
    type: Literal['Point']
    coordinates: List[float]


class VenueResponse(BaseModel):
    venue_id: int
    venue_organizer_id: int
    venue_name: str
    venue_type: Optional[str] = None
    venue_street: Optional[str] = None
    venue_house_number: Optional[str] = None
    venue_postal_code: Optional[str] = None
    venue_city: Optional[str] = None
    venue_opened_at: Optional[date] = None
    venue_closed_at: Optional[date] = None
    venue_organizer_name: Optional[str] = None
    venue_organizer_url: Optional[str] = None
    geojson: Optional[VenueGeoJSONPoint] = None

    @field_validator('venue_id')
    def validate_user_password(cls, value):
        return validate_positive_int32(value)


class UserVenueResponse(BaseModel):
    venue_id: int
    venue_name: str
    venue_organizer_id: int
    can_edit_venue: bool
    can_edit_space: bool
    can_edit_event: bool

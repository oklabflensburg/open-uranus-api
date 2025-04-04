from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List, Optional

from app.schemas.venue_response import VenueGeoJSONPoint


class EventUpdate(BaseModel):
    event_id: int
    event_title: Optional[str] = None
    event_description: Optional[str] = None
    event_venue_id: Optional[int] = None
    event_space_id: Optional[int] = None
    event_date_start: Optional[datetime] = None
    event_date_end: Optional[datetime] = None


class UserEventResponse(BaseModel):
    event_id: int
    event_date_id: int
    event_title: str
    event_date_start_first: datetime
    event_date_start_last: datetime
    event_venue_name: str
    can_edit: bool


class EventCreate(BaseModel):
    event_title: str
    event_description: str
    event_organizer_id: int
    event_venue_id: int
    event_space_id: Optional[int] = None
    event_date_start: datetime
    event_date_end: Optional[datetime] = None

    @field_validator('event_date_end', mode='before')
    def set_event_date_end(cls, v):
        return v or None


class EventResponse(BaseModel):
    event_id: int
    event_date_id: int
    event_title: str
    event_description: str
    event_organizer_id: int
    event_genre_type_id: List[int]
    event_venue_id: int
    event_space_id: Optional[int] = None
    event_date_start: datetime
    event_date_end: Optional[datetime] = None
    geojson: Optional[VenueGeoJSONPoint] = None


class EventQueryResponse(BaseModel):
    event_id: int
    event_date_id: int
    venue_id: int
    venue_name: str
    venue_postcode: str
    venue_city: str
    event_title: str
    event_description: str
    event_date_start: datetime
    event_created_at: datetime
    image_url: Optional[str] = None
    organizer_name: Optional[str] = None
    event_type: Optional[str] = None
    genre_type: Optional[str] = None
    venue_type: Optional[str] = None
    space_name: Optional[str] = None
    space_type: Optional[str] = None
    geojson: Optional[VenueGeoJSONPoint] = None

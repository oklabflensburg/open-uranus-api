from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional



class UserEventResponse(BaseModel):
    event_id: int
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
    event_title: str
    event_description: str
    event_organizer_id: int
    event_venue_id: int
    event_space_id: Optional[int] = None
    event_date_start: datetime
    event_date_end: Optional[datetime] = None



class EventQueryResponse(BaseModel):
    event_id: int 
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

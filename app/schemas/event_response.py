from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional



class EventResponse(BaseModel):
    event_id: int
    venue_type_id: Optional[int] = None
    space_type_id: Optional[int] = None
    genre_type_id: Optional[int] = None
    venue_name: str
    venue_postcode: str
    venue_city: str
    event_title: str
    event_description: str
    event_date_start: datetime
    organizer_name: Optional[str] = None
    event_type: Optional[str] = None
    genre_type: Optional[str] = None
    venue_type: Optional[str] = None
    space_name: Optional[str] = None
    space_type: Optional[str] = None

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional



class EventResponse(BaseModel):
    event_id: int
    event_title: str
    event_description: str
    organizer_name: Optional[str]
    event_type: Optional[str]
    genre_type: Optional[str]
    venue_type: Optional[str]
    venue_name: str
    venue_city: str
    date_start: datetime
    space_name: str

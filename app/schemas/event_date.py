from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class EventDateResponse(BaseModel):
    event_id: int
    event_space_id: int
    event_venue_id: int
    event_type_ids: Optional[List[int]]
    event_venue_type_id: int
    event_genre_type_ids: Optional[List[int]]
    event_title: str
    event_description: str
    event_date_start: datetime
    event_organizer_id: int
    event_image_url: Optional[str]

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional



class EventResponse(BaseModel):
    title: str
    description: str
    venue_name: str
    city: str
    start_date: datetime
    space_name: str
    ramp: Optional[bool]
    venue_type: str

from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime, date



class VenueJunkResponse(BaseModel):
    venue_id: int
    venue_name: str

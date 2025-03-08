from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date



class VenueURL(SQLModel, table=True):
    __tablename__ = 'venue_url'
    __table_args__ = {'schema': 'uranus'}

    id: int = Field(primary_key=True)
    venue_id: int = Field(foreign_key='uranus.venue.id')
    link_type: Optional[str] = Field(max_length=255, default=None)
    url: str
    title: Optional[str] = Field(max_length=255, default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = None

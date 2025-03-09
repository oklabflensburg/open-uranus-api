from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date



class EventBase(SQLModel):
    organizer_id: int = Field(foreign_key='uranus.organizer.id')
    venue_id: int = Field(foreign_key='uranus.venue.id')
    space_id: Optional[int] = Field(foreign_key='uranus.space.id', default=None)
    title: str = Field(max_length=255)
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = None




class Event(EventBase, table=True):
    __tablename__ = 'event'
    __table_args__ = {'schema': 'uranus'}

    id: Optional[int] = Field(default=None, primary_key=True)

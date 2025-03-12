from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, time, timezone



class EventDateBase(SQLModel):
    event_id: int = Field(foreign_key='uranus.event.id')
    venue_id: int = Field(foreign_key='uranus.venue.id')
    space_id: Optional[int] = Field(foreign_key='uranus.space.id', default=None)
    date_start: datetime
    date_end: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: Optional[datetime] = Field(default=None)
    entry_time: Optional[time] = Field(default=None)



class EventDate(EventDateBase, table=True):
    __tablename__ = 'event_date'
    __table_args__ = {'schema': 'uranus'}

    id: Optional[int] = Field(default=None, primary_key=True)

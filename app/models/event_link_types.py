from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

from app.models.event_type import EventType



class EventLinkTypes(SQLModel, table=True):
    __tablename__ = 'event_link_types'
    __table_args__ = {'schema': 'uranus'}

    event_id: int = Field(foreign_key='uranus.event.id', primary_key=True)
    event_type_id: int = Field(foreign_key='uranus.event_type.id', primary_key=True)

    event_type: Optional[EventType] = Relationship(back_populates='event_links')
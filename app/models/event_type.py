from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone



class EventTypeBase(SQLModel):
    i18n_locale_id: int = Field(foreign_key='uranus.i18n_locale.id', nullable=False)
    name: str = Field(nullable=False)
    type_id: int = Field(nullable=False)



class EventType(EventTypeBase, table=True):
    __tablename__ = 'event_type'
    __table_args__ = {'schema': 'uranus'}

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None
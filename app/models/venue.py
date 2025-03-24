from geoalchemy2 import Geometry
from sqlalchemy import Column
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date


class VenueBase(SQLModel):
    organizer_id: Optional[int] = Field(foreign_key='uranus.organizer.id')
    name: str = Field(max_length=255)
    street: Optional[str] = Field(max_length=255, default=None)
    house_number: Optional[str] = Field(max_length=50, default=None)
    postal_code: Optional[str] = Field(max_length=20, default=None)
    city: Optional[str] = Field(max_length=100, default=None)
    country_code: Optional[str] = Field(max_length=2, default=None)
    state_code: Optional[str] = Field(max_length=10, default=None)
    opened_at: Optional[date] = Field(default=None)
    closed_at: Optional[date] = Field(default=None)
    wkb_geometry: Optional[Geometry] = Field(
        sa_column=Column(Geometry('POINT', srid=4326)), default=None)

    class Config:
        arbitrary_types_allowed = True


class Venue(VenueBase, table=True):
    __tablename__ = 'venue'
    __table_args__ = {'schema': 'uranus'}

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None

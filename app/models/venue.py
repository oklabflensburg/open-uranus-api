from geoalchemy2 import Geometry
from sqlalchemy import Column
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date, timezone



class VenueBase(SQLModel):
    organizer_id: Optional[int] = Field(foreign_key='uranus.organizer.id')
    name: str = Field(max_length=255)
    street: Optional[str] = Field(max_length=255, default=None)
    house_number: Optional[str] = Field(max_length=50, default=None)
    postal_code: Optional[str] = Field(max_length=20, default=None)
    city: Optional[str] = Field(max_length=100, default=None)
    country_code: Optional[str] = Field(max_length=3, default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    opened_at: Optional[date] = Field(default=None)
    closed_at: Optional[date] = Field(default=None)
    wkb_geometry: Geometry = Field(sa_column=Column(Geometry('POINT', srid=4326)))

    class Config:
        arbitrary_types_allowed = True



class Venue(VenueBase, table=True):
    __tablename__ = 'venue'
    __table_args__ = {'schema': 'uranus'}

    id: Optional[int] = Field(default=None, primary_key=True)
    modified_at: Optional[datetime] = Field(default=None)
    county_code: Optional[str] = Field(max_length=10, default=None)

from geoalchemy2 import Geometry
from sqlalchemy import Column
from sqlmodel import SQLModel, Field
from typing import Optional
from shapely.geometry import Point
from datetime import datetime, date



class Venue(SQLModel, table=True):
    __tablename__ = 'venue'
    __table_args__ = {'schema': 'uranus'}

    id: int = Field(primary_key=True)
    organizer_id: Optional[int] = Field(foreign_key='uranus.organizer.id')
    name: str = Field(max_length=255)
    street: Optional[str] = Field(max_length=255, default=None)
    house_number: Optional[str] = Field(max_length=50, default=None)
    postal_code: Optional[str] = Field(max_length=20, default=None)
    city: Optional[str] = Field(max_length=100, default=None)
    country_code: Optional[str] = Field(max_length=3, default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = Field(default=None)
    county_code: Optional[str] = Field(max_length=10, default=None)
    opened_at: Optional[date] = Field(default=None)
    closed_at: Optional[date] = Field(default=None)
    wkb_geometry: Geometry = Field(sa_column=Column(Geometry('POINT', srid=4326)))

    class Config:
        arbitrary_types_allowed = True

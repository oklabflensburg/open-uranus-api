from geoalchemy2.shape import to_shape
from geoalchemy2 import Geometry
from sqlalchemy import Column
from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from typing import Optional
from shapely.geometry import Point
import json
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



class VenueResponse(BaseModel):
    id: int
    organizer_id: Optional[int]
    name: str
    street: Optional[str]
    house_number: Optional[str]
    postal_code: Optional[str]
    city: Optional[str]
    country_code: Optional[str]
    created_at: datetime
    modified_at: Optional[datetime]
    county_code: Optional[str]
    opened_at: Optional[date]
    closed_at: Optional[date]
    geojson: Optional[dict]

    @classmethod
    def from_orm(cls, venue: Venue):
        # Convert the geometry field to a Shapely geometry object
        geom = to_shape(venue.wkb_geometry)

        # Convert the Shapely geometry object to GeoJSON
        geojson = geom.__geo_interface__ if geom else None

        # Return the VenueResponse with GeoJSON formatted geometry
        return cls(**venue.dict(), geojson=geojson)

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, List, Optional

from sqlalchemy import ARRAY, Boolean, CHAR, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Identity, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, Time, text
from geoalchemy2 import Geometry
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.sqltypes import NullType
from sqlmodel import Field, Relationship, SQLModel

from app.schemas.space import Space
from app.schemas.organizer import Organizer
from app.schemas.venue_type import VenueType
from app.schemas.venue_url import VenueUrl
from app.schemas.event import Event
from app.schemas.event_date import EventDate



metadata = SQLModel.metadata


class Venue(SQLModel, table=True):
    __table_args__ = (
        CheckConstraint('char_length(country_code::text) = 3', name='country_length_check'),
        ForeignKeyConstraint(['organizer_id'], ['uranus.organizer.id'], name='venue_organizer_id_fkey'),
        PrimaryKeyConstraint('id', name='venue_pkey'),
        {'schema': 'uranus'}
    )

    id: Optional[int] = Field(default=None, sa_column=mapped_column('id', Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1)))
    name: str = Field(sa_column=mapped_column('name', String(255), nullable=False))
    created_at: datetime = Field(sa_column=mapped_column('created_at', DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP')))
    # wkb_geometry: Optional[Geometry] = Field(sa_column=mapped_column('wkb_geometry', Geometry('POINT', srid=4326), nullable=False))
    organizer_id: Optional[int] = Field(default=None, sa_column=mapped_column('organizer_id', Integer))
    street: Optional[str] = Field(default=None, sa_column=mapped_column('street', String(255)))
    house_number: Optional[str] = Field(default=None, sa_column=mapped_column('house_number', String(50)))
    postal_code: Optional[str] = Field(default=None, sa_column=mapped_column('postal_code', String(20)))
    city: Optional[str] = Field(default=None, sa_column=mapped_column('city', String(100)))
    country_code: Optional[str] = Field(default=None, sa_column=mapped_column('country_code', CHAR(3)))
    modified_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('modified_at', DateTime(True)))
    county_code: Optional[str] = Field(default=None, sa_column=mapped_column('county_code', String(10)))
    opened_at: Optional[date] = Field(default=None, sa_column=mapped_column('opened_at', Date))
    closed_at: Optional[date] = Field(default=None, sa_column=mapped_column('closed_at', Date))

    organizer: Optional['Organizer'] = Relationship(back_populates='venue')
    space: List['Space'] = Relationship(back_populates='venue')
    venue_url: List['VenueUrl'] = Relationship(back_populates='venue')
    event: List['Event'] = Relationship(back_populates='venue')
    event_date: List['EventDate'] = Relationship(back_populates='venue')

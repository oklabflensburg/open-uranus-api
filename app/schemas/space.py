from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, List, Optional

from sqlalchemy import ARRAY, Boolean, CHAR, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Identity, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, Time, text
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.sqltypes import NullType
from sqlmodel import Field, Relationship, SQLModel

metadata = SQLModel.metadata



class Space(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['venue_id'], ['uranus.venue.id'], ondelete='CASCADE', name='space_venue_id_fkey'),
        PrimaryKeyConstraint('id', name='space_pkey'),
        {'schema': 'uranus'}
    )

    id: Optional[int] = Field(default=None, sa_column=mapped_column('id', Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1)))
    venue_id: int = Field(sa_column=mapped_column('venue_id', Integer, nullable=False))
    name: str = Field(sa_column=mapped_column('name', String(255), nullable=False))
    created_at: datetime = Field(sa_column=mapped_column('created_at', DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP')))
    total_capacity: Optional[int] = Field(default=None, sa_column=mapped_column('total_capacity', Integer))
    seating_capacity: Optional[int] = Field(default=None, sa_column=mapped_column('seating_capacity', Integer))
    space_type_id: Optional[int] = Field(default=None, sa_column=mapped_column('space_type_id', Integer))
    building_level: Optional[int] = Field(default=None, sa_column=mapped_column('building_level', Integer))
    platform_lift: Optional[str] = Field(default=None, sa_column=mapped_column('platform_lift', String(255)))
    wheelchair: Optional[str] = Field(default=None, sa_column=mapped_column('wheelchair', Text))
    toilets: Optional[str] = Field(default=None, sa_column=mapped_column('toilets', Text))
    elevator: Optional[str] = Field(default=None, sa_column=mapped_column('elevator', Text))
    ramp: Optional[str] = Field(default=None, sa_column=mapped_column('ramp', Text))
    tactile_guidance: Optional[str] = Field(default=None, sa_column=mapped_column('tactile_guidance', Text))
    accessibility_info: Optional[str] = Field(default=None, sa_column=mapped_column('accessibility_info', Text))
    personalized_accessibility_services: Optional[bool] = Field(default=None, sa_column=mapped_column('personalized_accessibility_services', Boolean))
    wheelchair_friendly_surface: Optional[str] = Field(default=None, sa_column=mapped_column('wheelchair_friendly_surface', Text))
    quiet_zones: Optional[str] = Field(default=None, sa_column=mapped_column('quiet_zones', Text))
    url: Optional[str] = Field(default=None, sa_column=mapped_column('url', Text))
    floor_plan: Optional[str] = Field(default=None, sa_column=mapped_column('floor_plan', Text))
    tech_rider: Optional[str] = Field(default=None, sa_column=mapped_column('tech_rider', Text))
    modified_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('modified_at', DateTime(True)))
    area: Optional[Decimal] = Field(default=None, sa_column=mapped_column('area', Numeric))

    venue: Optional['Venue'] = Relationship(back_populates='space')
    event: List['Event'] = Relationship(back_populates='space')
    event_date: List['EventDate'] = Relationship(back_populates='space')


t_venue_link_types = Table(
    'venue_link_types', metadata,
    Column('venue_id', Integer, nullable=False),
    Column('venue_type_id', Integer, nullable=False),
    ForeignKeyConstraint(['venue_id'], ['uranus.venue.id'], ondelete='CASCADE', name='venue_link_types_venue_id_fkey'),
    ForeignKeyConstraint(['venue_type_id'], ['uranus.venue_type.id'], ondelete='CASCADE', name='venue_link_types_venue_type_id_fkey'),
    PrimaryKeyConstraint('venue_id', 'venue_type_id', name='venue_link_types_pkey'),
    schema='uranus'
)

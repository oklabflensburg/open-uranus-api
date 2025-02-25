from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, List, Optional

from sqlalchemy import ARRAY, Boolean, CHAR, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Identity, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, Time, text
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.sqltypes import NullType
from sqlmodel import Field, Relationship, SQLModel

metadata = SQLModel.metadata


class Event(SQLModel, table=True):
    __table_args__ = (
        ForeignKeyConstraint(['organizer_id'], ['uranus.organizer.id'], ondelete='CASCADE', name='event_organizer_id_fkey'),
        ForeignKeyConstraint(['space_id'], ['uranus.space.id'], ondelete='SET NULL', name='event_space_id_fkey'),
        ForeignKeyConstraint(['venue_id'], ['uranus.venue.id'], ondelete='CASCADE', name='event_venue_id_fkey'),
        PrimaryKeyConstraint('id', name='event_pkey'),
        {'schema': 'uranus'}
    )

    id: Optional[int] = Field(default=None, sa_column=mapped_column('id', Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1)))
    organizer_id: int = Field(sa_column=mapped_column('organizer_id', Integer, nullable=False))
    venue_id: int = Field(sa_column=mapped_column('venue_id', Integer, nullable=False))
    title: str = Field(sa_column=mapped_column('title', String(255), nullable=False))
    description: str = Field(sa_column=mapped_column('description', Text, nullable=False))
    created_at: datetime = Field(sa_column=mapped_column('created_at', DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP')))
    space_id: Optional[int] = Field(default=None, sa_column=mapped_column('space_id', Integer))
    modified_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('modified_at', DateTime(True)))

    organizer: Optional['Organizer'] = Relationship(back_populates='event')
    space: Optional['Space'] = Relationship(back_populates='event')
    venue: Optional['Venue'] = Relationship(back_populates='event')
    event_date: List['EventDate'] = Relationship(back_populates='event')

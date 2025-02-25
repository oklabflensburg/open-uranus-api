from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, List, Optional

from sqlalchemy import ARRAY, Boolean, CHAR, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Identity, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, Time, text
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.sqltypes import NullType
from sqlmodel import Field, Relationship, SQLModel

metadata = SQLModel.metadata



class EventDate(SQLModel, table=True):
    __tablename__ = 'event_date'
    __table_args__ = (
        ForeignKeyConstraint(['event_id'], ['uranus.event.id'], ondelete='CASCADE', name='event_date_event_id_fkey'),
        ForeignKeyConstraint(['space_id'], ['uranus.space.id'], ondelete='SET NULL', name='event_date_space_id_fkey'),
        ForeignKeyConstraint(['venue_id'], ['uranus.venue.id'], ondelete='CASCADE', name='event_date_venue_id_fkey'),
        PrimaryKeyConstraint('id', name='event_date_pkey'),
        {'schema': 'uranus'}
    )

    id: Optional[int] = Field(default=None, sa_column=mapped_column('id', Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1)))
    event_id: int = Field(sa_column=mapped_column('event_id', Integer, nullable=False))
    venue_id: int = Field(sa_column=mapped_column('venue_id', Integer, nullable=False))
    start_date: datetime = Field(sa_column=mapped_column('start_date', DateTime(True), nullable=False))
    created_at: datetime = Field(sa_column=mapped_column('created_at', DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP')))
    space_id: Optional[int] = Field(default=None, sa_column=mapped_column('space_id', Integer))
    end_date: Optional[datetime] = Field(default=None, sa_column=mapped_column('end_date', DateTime(True)))
    modified_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('modified_at', DateTime(True)))
    entry_time: Optional[time] = Field(default=None, sa_column=mapped_column('entry_time', Time(True)))

    event: Optional['Event'] = Relationship(back_populates='event_date')
    space: Optional['Space'] = Relationship(back_populates='event_date')
    venue: Optional['Venue'] = Relationship(back_populates='event_date')

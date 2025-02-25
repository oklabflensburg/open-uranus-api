from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, List, Optional

from sqlalchemy import ARRAY, Boolean, CHAR, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Identity, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, Time, text
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.sqltypes import NullType
from sqlmodel import Field, Relationship, SQLModel

metadata = SQLModel.metadata



class VenueUrl(SQLModel, table=True):
    __tablename__ = 'venue_url'
    __table_args__ = (
        ForeignKeyConstraint(['venue_id'], ['uranus.venue.id'], ondelete='CASCADE', name='venue_url_venue_id_fkey'),
        PrimaryKeyConstraint('id', name='venue_url_pkey'),
        {'schema': 'uranus'}
    )

    id: Optional[int] = Field(default=None, sa_column=mapped_column('id', Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1)))
    venue_id: int = Field(sa_column=mapped_column('venue_id', Integer, nullable=False))
    url: str = Field(sa_column=mapped_column('url', Text, nullable=False))
    created_at: datetime = Field(sa_column=mapped_column('created_at', DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP')))
    link_type: Optional[str] = Field(default=None, sa_column=mapped_column('link_type', String(255)))
    title: Optional[str] = Field(default=None, sa_column=mapped_column('title', String(255)))
    modified_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('modified_at', DateTime(True)))

    venue: Optional['Venue'] = Relationship(back_populates='venue_url')

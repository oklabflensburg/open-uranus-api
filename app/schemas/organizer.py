from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, List, Optional

from sqlalchemy import ARRAY, Boolean, CHAR, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Identity, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, Time, text
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.sqltypes import NullType
from sqlmodel import Field, Relationship, SQLModel

metadata = SQLModel.metadata



class Organizer(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='organizer_pkey'),
        {'schema': 'uranus'}
    )

    id: Optional[int] = Field(default=None, sa_column=mapped_column('id', Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1)))
    name: str = Field(sa_column=mapped_column('name', String(255), nullable=False))
    created_at: datetime = Field(sa_column=mapped_column('created_at', DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP')))
    description: Optional[str] = Field(default=None, sa_column=mapped_column('description', Text))
    contact_email: Optional[str] = Field(default=None, sa_column=mapped_column('contact_email', String(255)))
    contact_phone: Optional[str] = Field(default=None, sa_column=mapped_column('contact_phone', String(50)))
    website_url: Optional[str] = Field(default=None, sa_column=mapped_column('website_url', Text))
    street: Optional[str] = Field(default=None, sa_column=mapped_column('street', String(255)))
    house_number: Optional[str] = Field(default=None, sa_column=mapped_column('house_number', String(50)))
    postal_code: Optional[str] = Field(default=None, sa_column=mapped_column('postal_code', String(20)))
    city: Optional[str] = Field(default=None, sa_column=mapped_column('city', String(100)))
    country: Optional[str] = Field(default=None, sa_column=mapped_column('country', String(100)))
    modified_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('modified_at', DateTime(True)))

    venue: List['Venue'] = Relationship(back_populates='organizer')
    event: List['Event'] = Relationship(back_populates='organizer')

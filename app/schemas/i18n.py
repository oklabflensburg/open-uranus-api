from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, List, Optional

from sqlalchemy import ARRAY, Boolean, CHAR, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Identity, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, Time, text
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.sqltypes import NullType
from sqlmodel import Field, Relationship, SQLModel



metadata = SQLModel.metadata


class I18n(SQLModel, table=True):
    __table_args__ = (
        PrimaryKeyConstraint('id', name='i18n_pkey'),
        {'schema': 'uranus'}
    )

    id: Optional[int] = Field(default=None, sa_column=mapped_column('id', Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1)))
    iso_code_alpha_3: str = Field(sa_column=mapped_column('iso_code_alpha_3', String(10), nullable=False))
    created_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('created_at', DateTime(True), server_default=text('CURRENT_TIMESTAMP')))
    modified_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('modified_at', DateTime(True)))

    #space_type: List['SpaceType'] = Relationship(back_populates='i18n')
    #venue_type: List['VenueType'] = Relationship(back_populates='i18n')

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, List, Optional

from sqlalchemy import ARRAY, Boolean, CHAR, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Identity, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, Time, text
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.sqltypes import NullType
from sqlmodel import Field, Relationship, SQLModel



metadata = SQLModel.metadata

class VenueType(SQLModel, table=True):
    __tablename__ = 'venue_type'
    __table_args__ = (
        ForeignKeyConstraint(['i18n_id'], ['uranus.i18n.id'], ondelete='CASCADE', name='venue_type_i18n_id_fkey'),
        PrimaryKeyConstraint('id', name='venue_type_pkey'),
        {'schema': 'uranus'}
    )

    id: Optional[int] = Field(default=None, sa_column=mapped_column('id', Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1)))
    i18n_id: int = Field(sa_column=mapped_column('i18n_id', Integer, nullable=False))
    type_name: str = Field(sa_column=mapped_column('type_name', Text, nullable=False))

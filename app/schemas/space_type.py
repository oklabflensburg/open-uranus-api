from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, List, Optional

from sqlalchemy import ARRAY, Boolean, CHAR, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Identity, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, Time, text
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.sqltypes import NullType
from sqlmodel import Field, Relationship, SQLModel

from app.schemas.i18n import I18n

metadata = SQLModel.metadata




class SpaceType(SQLModel, table=True):
    __tablename__ = 'space_type'
    __table_args__ = (
        ForeignKeyConstraint(['i18n_id'], ['uranus.i18n.id'], ondelete='CASCADE', name='space_type_i18n_id_fkey'),
        PrimaryKeyConstraint('id', name='space_type_pkey'),
        {'schema': 'uranus'}
    )

    id: Optional[int] = Field(default=None, sa_column=mapped_column('id', Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1)))
    i18n_id: int = Field(sa_column=mapped_column('i18n_id', Integer, nullable=False))
    name: str = Field(sa_column=mapped_column('name', Text, nullable=False))
    created_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('created_at', DateTime(True), server_default=text('CURRENT_TIMESTAMP')))
    modified_at: Optional[datetime] = Field(default=None, sa_column=mapped_column('modified_at', DateTime(True)))

    i18n: Optional['I18n'] = Relationship(back_populates='space_type')

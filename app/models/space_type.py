from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime



class SpaceType(SQLModel, table=True):
    __tablename__ = 'space_type'
    __table_args__ = {'schema': 'uranus'}

    id: int = Field(primary_key=True)
    i18n_locale_id: int = Field(foreign_key='uranus.i18n_locale.id', nullable=False)
    name: str = Field(nullable=False)
    type_id: str = Field(nullable=False)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = None

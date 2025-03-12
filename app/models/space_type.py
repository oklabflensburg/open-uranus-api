from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timezone



class SpaceTypeBase(SQLModel):
    i18n_locale_id: int = Field(foreign_key='uranus.i18n_locale.id', nullable=False)
    name: str = Field(nullable=False)
    type_id: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None



class SpaceType(SpaceTypeBase, table=True):
    __tablename__ = 'space_type'
    __table_args__ = {'schema': 'uranus'}

    id: Optional[int] = Field(default=None, primary_key=True)

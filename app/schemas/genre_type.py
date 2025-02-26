from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

#from app.schemas.genre_link_types import GenreLinkTypes



class GenreType(SQLModel, table=True):
    __tablename__ = 'genre_type'
    __table_args__ = {'schema': 'uranus'}

    id: int = Field(primary_key=True)
    i18n_locale_id: int = Field(foreign_key='uranus.i18n_locale.id', nullable=False)
    name: str = Field(nullable=False)
    type_id: int = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    modified_at: Optional[datetime] = None

    #genre_links: List['GenreLinkTypes'] = Relationship(back_populates='genre_type')
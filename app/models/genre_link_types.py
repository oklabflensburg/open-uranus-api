from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

#from app.schemas.genre_type import GenreType



class GenreLinkTypes(SQLModel, table=True):
    __tablename__ = 'genre_link_types'
    __table_args__ = {'schema': 'uranus'}

    event_id: int = Field(foreign_key='uranus.event.id', primary_key=True)
    genre_type_id: int = Field(foreign_key='uranus.genre_type.id', primary_key=True)

    #genre_type: Optional[GenreType] = Relationship(back_populates='genre_links')
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional



class SpaceBase(SQLModel):
    venue_id: int = Field(index=True, nullable=False)
    name: str = Field(max_length=255, nullable=False)
    total_capacity: int | None = None
    total_capacity: Optional[int] = None
    seating_capacity: Optional[int] = None
    space_type_id: Optional[int] = None
    building_level: Optional[int] = None
    url: Optional[str] = None



class Space(SpaceBase, table=True):
    __tablename__ = 'space'
    __table_args__ = {'schema': 'uranus'}

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None
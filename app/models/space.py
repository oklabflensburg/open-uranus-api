from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date



class SpaceBase(SQLModel):
    venue_id: int = Field(foreign_key='uranus.venue.id')
    name: str = Field(max_length=255)
    total_capacity: Optional[int] = None
    seating_capacity: Optional[int] = None
    space_type_id: Optional[int] = None
    building_level: Optional[int] = None
    platform_lift: Optional[str] = Field(max_length=255, default=None)
    wheelchair: Optional[str] = None
    toilets: Optional[str] = None
    elevator: Optional[str] = None
    ramp: Optional[str] = None
    tactile_guidance: Optional[str] = None
    accessibility_info: Optional[str] = None
    personalized_accessibility_services: Optional[bool] = None
    wheelchair_friendly_surface: Optional[str] = None
    quiet_zones: Optional[str] = None
    url: Optional[str] = None
    floor_plan: Optional[str] = None
    tech_rider: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = None
    area: Optional[float] = None



class Space(SpaceBase, table=True):
    __tablename__ = 'space'
    __table_args__ = {'schema': 'uranus'}

    id: Optional[int] = Field(default=None, primary_key=True)

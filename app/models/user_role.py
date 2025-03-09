from typing import Optional

from sqlmodel import SQLModel, Field



class UserRoleBase(SQLModel):
    name: str
    organization: bool
    venue: bool
    space: bool
    event: bool
    image_type: bool
    venue_type: bool
    event_type: bool
    license_type: bool
    genre_type: bool
    space_type: bool
    role_type: bool



class UserRole(UserRoleBase, table=True):
  __tablename__ = 'user_role'
  __table_args__ = {'schema': 'uranus'}

  id: Optional[int] = Field(default=None, primary_key=True)

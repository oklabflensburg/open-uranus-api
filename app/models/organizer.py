from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class OrganizerBase(SQLModel):
    name: str = Field(max_length=255)
    description: Optional[str] = None
    contact_email: Optional[str] = Field(default=None, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=50)
    website_url: Optional[str] = None
    street: Optional[str] = Field(default=None, max_length=255)
    house_number: Optional[str] = Field(default=None, max_length=50)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    city: Optional[str] = Field(default=None, max_length=100)


class Organizer(OrganizerBase, table=True):
    __tablename__ = 'organizer'
    __table_args__ = {'schema': 'uranus'}

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None

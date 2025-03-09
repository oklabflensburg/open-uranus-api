from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime



class OrganizerBase(SQLModel):
    name: str = Field(max_length=255)
    description: Optional[str] = None
    contact_email: Optional[str] = Field(max_length=255, default=None)
    contact_phone: Optional[str] = Field(max_length=50, default=None)
    website_url: Optional[str] = None
    street: Optional[str] = Field(max_length=255, default=None)
    house_number: Optional[str] = Field(max_length=50, default=None)
    postal_code: Optional[str] = Field(max_length=20, default=None)
    city: Optional[str] = Field(max_length=100, default=None)
    country: Optional[str] = Field(max_length=100, default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: Optional[datetime] = None



class Organizer(OrganizerBase, table=True):
    __tablename__ = 'organizer'
    __table_args__ = {'schema': 'uranus'}

    id: Optional[int] = Field(default=None, primary_key=True)

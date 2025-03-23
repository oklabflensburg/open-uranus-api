from pydantic import BaseModel, EmailStr
from typing import Optional


class UserOrganizerResponse(BaseModel):
    organizer_id: int
    organizer_name: str
    can_edit: bool


class OrganizerSchema(BaseModel):
    organizer_id: int
    organizer_name: str
    organizer_description: Optional[str]
    organizer_contact_email: Optional[EmailStr]
    organizer_contact_phone: Optional[str]
    organizer_website_url: Optional[str]
    organizer_street: Optional[str]
    organizer_house_number: Optional[str]
    organizer_postal_code: Optional[str]
    organizer_city: Optional[str]


class OrganizerCreate(BaseModel):
    organizer_name: str
    organizer_description: Optional[str]
    organizer_contact_email: Optional[EmailStr]
    organizer_contact_phone: Optional[str]
    organizer_website_url: Optional[str]
    organizer_street: Optional[str]
    organizer_house_number: Optional[str]
    organizer_postal_code: Optional[str]
    organizer_city: Optional[str]


class OrganizerRead(BaseModel):
    organizer_id: int
    organizer_name: str

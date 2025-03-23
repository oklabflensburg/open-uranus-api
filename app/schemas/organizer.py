from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class UserOrganizerResponse(BaseModel):
    organizer_id: int
    organizer_name: str
    can_edit: bool


class OrganizerCreate(BaseModel):
    organizer_name: str
    organizer_description: Optional[str] = None
    organizer_contact_email: Optional[EmailStr] = None
    organizer_contact_phone: Optional[str] = None
    organizer_website_url: Optional[str] = None
    organizer_street: Optional[str] = None
    organizer_house_number: Optional[str] = None
    organizer_postal_code: Optional[str] = None
    organizer_city: Optional[str] = None
    organizer_holding_organizer_id: Optional[int] = None
    organizer_legal_form_id: Optional[int] = None
    organizer_nonprofit: Optional[bool] = None
    organizer_address_addition: Optional[str] = None

    @field_validator('organizer_contact_email', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v


class OrganizerSchema(OrganizerCreate):
    organizer_id: int


class OrganizerRead(BaseModel):
    organizer_id: int
    organizer_name: str

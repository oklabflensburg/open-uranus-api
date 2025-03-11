from pydantic import BaseModel, EmailStr



class OrganizerCreate(BaseModel):
    organizer_name: str
    organizer_description: str
    organizer_contact_email: EmailStr
    organizer_contact_phone: str
    organizer_website_url: str
    organizer_street: str
    organizer_house_number: str
    organizer_postal_code: str
    organizer_city: str



class OrganizerRead(BaseModel):
    organizer_id: int 
    organizer_name: str 

from pydantic import BaseModel



class OrganizerRead(BaseModel):
    organizer_id: int 
    organizer_name: str 

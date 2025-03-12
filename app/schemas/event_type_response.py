from pydantic import BaseModel



class EventTypeResponse(BaseModel):
    event_type_id: int
    event_type_name: str
    event_locale_id: int

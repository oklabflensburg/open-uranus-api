from pydantic import BaseModel


class StateResponse(BaseModel):
    state_name: str
    state_code: str
    state_country_code: str

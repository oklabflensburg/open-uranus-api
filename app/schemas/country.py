from pydantic import BaseModel


class CountryResponse(BaseModel):
    country_name: str
    country_code: str
    country_iso_639_1: str

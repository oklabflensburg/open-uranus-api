from pydantic import BaseModel



class GenreTypeResponse(BaseModel):
    genre_type_id: int
    genre_type_name: str
    genre_locale_id: int

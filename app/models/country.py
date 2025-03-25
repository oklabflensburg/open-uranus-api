from sqlmodel import SQLModel, Field


class Country(SQLModel, table=True):
    __tablename__ = 'country'
    __table_args__ = {'schema': 'uranus'}

    code: str = Field(..., max_length=3, primary_key=True)
    name: str = Field(..., nullable=False)
    iso_639_1: str = Field(..., max_length=2, nullable=False)

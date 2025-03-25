from sqlmodel import SQLModel, Field


class State(SQLModel, table=True):
    __tablename__ = 'state'
    __table_args__ = {'schema': 'uranus'}

    code: str = Field(..., max_length=2, primary_key=True)
    country_code: str = Field(..., max_length=3)
    name: str = Field(..., nullable=False)

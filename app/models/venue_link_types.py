from sqlmodel import SQLModel, Field



class VenueLinkTypes(SQLModel, table=True):
    __tablename__ = 'venue_link_types'
    __table_args__ = {'schema': 'uranus'}

    venue_id: int = Field(foreign_key='uranus.venue.id', primary_key=True)
    venue_type_id: int = Field(foreign_key='uranus.venue_type.id', primary_key=True)

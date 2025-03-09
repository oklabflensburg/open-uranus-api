from sqlmodel import SQLModel, Field



class UserVenueLinks(SQLModel, table=True):
    __tablename__ = 'user_venue_links'
    __table_args__ = {'schema': 'uranus'}

    user_id: int = Field(foreign_key='uranus.user.id', primary_key=True)
    venue_id: int = Field(foreign_key='uranus.venue.id', primary_key=True)
    user_role_id: int = Field(foreign_key='uranus.user_role.id', primary_key=True)
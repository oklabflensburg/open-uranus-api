from sqlmodel import SQLModel, Field


class UserOrganizerLinks(SQLModel, table=True):
    __tablename__ = 'user_organizer_links'
    __table_args__ = {'schema': 'uranus'}

    user_id: int = Field(foreign_key='uranus.user.id', primary_key=True)
    organizer_id: int = Field(
        foreign_key='uranus.organizer.id', primary_key=True)
    user_role_id: int = Field(
        foreign_key='uranus.user_role.id', nullable=False)

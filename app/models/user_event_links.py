from sqlmodel import SQLModel, Field


class UserEventLinks(SQLModel, table=True):
    __tablename__ = 'user_event_links'
    __table_args__ = {'schema': 'uranus'}

    user_id: int = Field(foreign_key='uranus.user.id', primary_key=True)
    event_id: int = Field(foreign_key='uranus.event.id', primary_key=True)
    user_role_id: int = Field(
        foreign_key='uranus.user_role.id', nullable=False)

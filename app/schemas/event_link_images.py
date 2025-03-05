from sqlmodel import SQLModel, Field
from typing import Optional



class EventLinkImages(SQLModel, table=True):
    __tablename__ = 'event_link_images'
    __table_args__ = {'schema': 'uranus'}

    event_id: int = Field(foreign_key='uranus.event.id', primary_key=True)
    image_id: int = Field(foreign_key='uranus.image.id', primary_key=True)
    main_image: Optional[bool] = Field(default=None)
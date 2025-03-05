from sqlmodel import SQLModel, Field
from typing import Optional



class EventDateLinkImages(SQLModel, table=True):
    __tablename__ = 'event_date_link_images'
    __table_args__ = {'schema': 'uranus'}

    event_date_id: int = Field(foreign_key='uranus.event_date.id', primary_key=True)
    image_id: int = Field(foreign_key='uranus.image.id', primary_key=True)
    main_image: Optional[bool] = Field(default=None)
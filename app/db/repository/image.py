from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_

from app.models.event_link_images import EventLinkImages
from app.models.image import Image


async def get_main_image_id_by_event_id(db: AsyncSession, event_id: int):
    print('event_id', event_id)
    stmt = (
        select(Image)
        .join(EventLinkImages, EventLinkImages.image_id == Image.id)
        .where(EventLinkImages.event_id == event_id)
    )

    result = await db.execute(stmt)
    image = result.mappings().first()

    print('PIPPPA', image)

    return image

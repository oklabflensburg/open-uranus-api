from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organizer import Organizer
from app.models.user_organizer_links import UserOrganizerLinks



async def get_organizer_by_user_id(db: AsyncSession, user_id: int):
    stmt = ( 
        select(
            Organizer.id.label('organizer_id'),
            Organizer.name.label('organizer_name')
        )
        .join(UserOrganizerLinks, UserOrganizerLinks.organizer_id == Organizer.id)
        .where(UserOrganizerLinks.user_id == user_id)
    )

    result = await db.execute(stmt)
    organizer = result.mappings().all()

    return organizer
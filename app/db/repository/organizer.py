from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organizer import Organizer
from app.models.user_organizer_links import UserOrganizerLinks

from app.schemas.organizer import OrganizerCreate



async def add_user_organizer_link(db: AsyncSession, user_id: int, organizer_id: int, user_role_id: int):
    new_user_organizer_link = UserOrganizerLinks(
        user_id=user_id,
        organizer_id=organizer_id,
        user_role_id=user_role_id
    )

    db.add(new_user_organizer_link)

    try:
        await db.commit()
        await db.refresh(new_user_organizer_link)

        return new_user_organizer_link
    except IntegrityError as e:
        await db.rollback()



async def add_organizer(db: AsyncSession, organizer: OrganizerCreate):
    new_organizer = Organizer(
        name=organizer.organizer_name,
        description=organizer.organizer_description,
        contact_email=organizer.organizer_contact_email,
        contact_phone=organizer.organizer_contact_phone,
        website_url=organizer.organizer_website_url,
        street=organizer.organizer_street,
        house_number=organizer.organizer_house_number,
        postal_code=organizer.organizer_postal_code,
        city=organizer.organizer_city
    )

    db.add(new_organizer)

    try:
        await db.commit()
        await db.refresh(new_organizer)

        return new_organizer
    except IntegrityError as e:
        await db.rollback()



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
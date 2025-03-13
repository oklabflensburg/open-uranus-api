from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from pydantic import EmailStr

from app.models.organizer import Organizer
from app.models.user_organizer_links import UserOrganizerLinks
from app.models.user_role import UserRole
from app.models.user import User
from app.models.venue import Venue
from app.models.space import Space

from app.schemas.organizer import OrganizerCreate



async def add_user_organizer(db: AsyncSession, user_id: int, organizer_id: int, user_role_id: int):
    new_user_organizer = UserOrganizerLinks(
        user_id=user_id,
        organizer_id=organizer_id,
        user_role_id=user_role_id
    )

    db.add(new_user_organizer)

    try:
        await db.commit()
        await db.refresh(new_user_organizer)

        return new_user_organizer
    except IntegrityError as e:
        await db.rollback()



async def add_organizer(db: AsyncSession, organizer: OrganizerCreate, current_user_email: EmailStr):
    new_organizer = Organizer(
        name=organizer.organizer_name,
        description=organizer.organizer_description,
        contact_email=current_user_email,
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



async def get_organizers_by_user_id(db: AsyncSession, user_id: int):
    stmt = (
        select(
            UserOrganizerLinks.organizer_id,
            Organizer.name.label('organizer_name'),
            UserRole.organization.label('can_edit')
        )
        .join(User, User.id == UserOrganizerLinks.user_id)
        .join(Organizer, Organizer.id == UserOrganizerLinks.organizer_id)
        .join(UserRole, UserRole.id == UserOrganizerLinks.user_role_id)
        .where(UserOrganizerLinks.user_id == user_id)
    )

    result = await db.execute(stmt)
    organizer = result.mappings().all()

    return organizer



async def get_organizer_stats(db: AsyncSession, organizer_id: int):
    stmt = (
        select(
            func.count(Venue.id.distinct()).label('count_venue'),
            func.count(Space.id).label('count_space')
        )
        .join(Organizer, Organizer.id == Venue.organizer_id)
        .outerjoin(Space, Space.venue_id == Venue.id)
        .where(Organizer.id == organizer_id)
    )

    result = await db.execute(stmt)
    stats = result.mappings().first()

    return stats
from fastapi import HTTPException, status

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, or_
from datetime import datetime
from pydantic import EmailStr
from typing import List

from app.models.organizer import Organizer
from app.models.user_organizer_links import UserOrganizerLinks
from app.models.user_role import UserRole
from app.models.user import User
from app.models.venue import Venue
from app.models.space import Space
from app.models.event import Event
from app.models.event_date import EventDate

from app.schemas.organizer import OrganizerCreate, OrganizerSchema


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
    except IntegrityError:
        await db.rollback()


async def get_organizer_by_id(db: AsyncSession, organizer_id: int):
    stmt = (
        select(Organizer).where(Organizer.id == organizer_id)
    )

    result = await db.execute(stmt)
    organizer = result.scalars().first()

    return organizer


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
        .order_by(Organizer.name)
    )

    result = await db.execute(stmt)
    organizer = result.mappings().all()

    return organizer


async def get_organizer_stats(db: AsyncSession, organizer_id: int):
    stmt = (
        select(
            func.count(func.distinct(Venue.id)).label('count_venues'),
            func.count(func.distinct(Space.id)).label('count_spaces'),
            func.coalesce(func.count(func.distinct(Event.id)),
                          0).label('count_events')
        )
        .select_from(Organizer)
        .join(Venue, Venue.organizer_id == Organizer.id)
        .outerjoin(Space, Space.venue_id == Venue.id)
        .outerjoin(Event, Event.venue_id == Venue.id)
        .outerjoin(EventDate, EventDate.event_id == Event.id)
        .filter(
            Organizer.id == organizer_id,
            or_(
                EventDate.date_start >= datetime.now(),
                EventDate.date_start == None
            )
        )
    )

    result = await db.execute(stmt)
    stats = result.mappings().first()

    return stats


async def delete_organizer_by_id(db: AsyncSession, organizer: Organizer):
    await db.delete(organizer)

    try:
        await db.commit()
        return True
    except IntegrityError:
        await db.rollback()
        return False


async def get_all_organizers(db: AsyncSession) -> List[OrganizerSchema]:
    stmt = select(Organizer).order_by(Organizer.name)

    result = await db.execute(stmt)
    organizers = result.scalars().all()

    return [
        OrganizerSchema(
            organizer_id=organizer.id,
            organizer_name=organizer.name,
            organizer_description=organizer.description,
            organizer_contact_email=organizer.contact_email,
            organizer_contact_phone=organizer.contact_phone,
            organizer_website_url=organizer.website_url,
            organizer_street=organizer.street,
            organizer_house_number=organizer.house_number,
            organizer_postal_code=organizer.postal_code,
            organizer_city=organizer.city,
            organizer_holding_organizer_id=organizer.holding_organizer_id,
            organizer_nonprofit=organizer.nonprofit,
            organizer_legal_form_id=organizer.legal_form_id,
            organizer_address_addition=organizer.address_addition
        )
        for organizer in organizers
    ]

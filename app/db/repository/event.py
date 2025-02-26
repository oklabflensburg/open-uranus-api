from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.future import select
from sqlalchemy.sql import func

from app.schemas.event import Event
from app.schemas.event_date import EventDate
from app.schemas.space import Space
from app.schemas.venue import Venue
from app.schemas.venue_link_types import VenueLinkTypes
from app.schemas.venue_type import VenueType


async def get_all_events(db: AsyncSession):
    result = await db.execute(select(Event))
    
    events = result.scalars().all()
    return events


async def get_all_detailed_events(db: AsyncSession, city: str):
    stmt = (
        select(
            Event.title,
            Event.description,
            Venue.name.label('venue_name'),
            Venue.city,
            EventDate.start_date,
            Space.name.label('space_name'),
            Space.ramp,
            func.string_agg(VenueType.type_name, ', ').label('venue_type'),
        )
        .join(EventDate, EventDate.event_id == Event.id)
        .join(Space, Space.id == EventDate.space_id)
        .join(Venue, Venue.id == Space.venue_id)
        .outerjoin(VenueLinkTypes, VenueLinkTypes.venue_id == Venue.id)
        .outerjoin(VenueType, VenueType.id == VenueLinkTypes.venue_type_id)
        .filter(EventDate.start_date >= func.now())
        .filter(Venue.city == city)
        .group_by(
            Event.title,
            Event.description,
            Venue.name,
            Venue.city,
            EventDate.start_date,
            Space.name,
            Space.ramp
        )
    )

    result = await db.execute(stmt)
    events = result.mappings().all()
    return events
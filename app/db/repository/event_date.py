import re

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import array_agg  # Add this import

from app.models.event_date import EventDate
from app.models.event import Event
from app.models.event_date_link_images import EventDateLinkImages
from app.models.event_link_images import EventLinkImages
from app.models.event_link_types import EventLinkTypes
from app.models.event_type import EventType
from app.models.genre_link_types import GenreLinkTypes
from app.models.genre_type import GenreType
from app.models.organizer import Organizer
from app.models.space import Space
from app.models.venue import Venue
from app.models.image import Image
from app.models.venue_link_types import VenueLinkTypes
from app.models.venue_type import VenueType
from app.schemas.event import EventCreate


async def add_event_date(
    db: AsyncSession,
    event: EventCreate,
    new_event: Event
):
    # Remove timezone information
    date_start = event.event_date_start.replace(tzinfo=None)
    date_end = event.event_date_end.replace(tzinfo=None) if event.event_date_end else None

    new_event_date = EventDate(
        date_start=date_start,
        date_end=date_end,
        event_id=new_event.id,
        venue_id=event.event_venue_id,
        space_id=event.event_space_id,
    )

    db.add(new_event_date)

    try:
        await db.commit()
        await db.refresh(new_event_date)
        return new_event_date
    except IntegrityError as e:
        await db.rollback()

        error_message = str(e.orig)
        match = re.search(r'\(([a-zA-Z_]+)\)=\((-?\d+)\)', error_message)

        if match:
            column_name = match.group(1)
            column_value = match.group(2)

            if column_name in ['venue_id', 'space_id', 'organizer_id']:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'The {column_name} ({column_value}) provided is invalid.',
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Foreign key constraint violation.',
            )


async def get_simple_event_date_by_id(db: AsyncSession, event_date_id: int):
    stmt = select(EventDate).where(EventDate.id == event_date_id)

    result = await db.execute(stmt)
    event = result.mappings().first()

    return event


async def get_event_by_event_date_id(
    db: AsyncSession,
    base_url: str,
    event_date_id: int,
    lang: str
):
    stmt = (
        select(
            Event.id.label('event_id'),
            Space.id.label('event_space_id'),
            Venue.id.label('event_venue_id'),
            array_agg(
                func.coalesce(EventType.id, None)
            ).filter(EventType.id.isnot(None)).label('event_type_ids'),
            VenueType.type_id.label('event_venue_type_id'),
            GenreType.type_id.label('event_genre_type_id'),
            Event.title.label('event_title'),
            Event.description.label('event_description'),
            EventDate.date_start.label('event_date_start'),
            Organizer.id.label('event_organizer_id'),
            func.nullif(
                func.concat(base_url, 'uploads/', Image.source_name),
                base_url + 'uploads/',
            ).label('event_image_url'),
        )
        .select_from(Event)
        .join(EventDate, Event.id == EventDate.event_id)
        .outerjoin(Venue, Venue.id == func.coalesce(
            EventDate.venue_id, Event.venue_id)
        )
        .outerjoin(Space, Space.id == func.coalesce(
            EventDate.space_id, Event.space_id)
        )
        .outerjoin(EventLinkTypes, EventLinkTypes.event_id == Event.id)
        .outerjoin(EventType, EventType.id == EventLinkTypes.event_type_id)
        .outerjoin(GenreLinkTypes, GenreLinkTypes.event_id == Event.id)
        .outerjoin(GenreType, GenreType.id == GenreLinkTypes.genre_type_id)
        .outerjoin(VenueLinkTypes, VenueLinkTypes.venue_id == Venue.id)
        .outerjoin(Organizer, Organizer.id == Event.organizer_id)
        .outerjoin(
            EventDateLinkImages,
            (EventDateLinkImages.event_date_id == EventDate.id)
            & (EventDateLinkImages.main_image.is_(True)),
        )
        .outerjoin(
            EventLinkImages,
            (EventLinkImages.event_id == Event.id)
            & (EventLinkImages.main_image.is_(True)),
        )
        .outerjoin(
            Image,
            Image.id == func.coalesce(
                EventDateLinkImages.image_id, EventLinkImages.image_id
            ),
        )
        .where(EventDate.id == event_date_id)
        .group_by(
            Event.id,
            Space.id,
            Venue.id,
            VenueType.type_id,
            GenreType.type_id,
            Event.title,
            Event.description,
            EventDate.date_start,
            Organizer.id,
            Image.source_name,
        )
    )

    result = await db.execute(stmt)
    event = result.mappings().first()

    return event

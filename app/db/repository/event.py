import re

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from sqlalchemy import asc, desc, or_, case, cast, JSON, exists
from geoalchemy2.functions import ST_AsGeoJSON

from app.models.user_organizer_links import UserOrganizerLinks
from app.schemas.event import EventCreate, EventUpdate
from app.schemas.image import ImageCreate

from app.models.i18n_locale import I18nLocale
from app.models.organizer import Organizer
from app.models.event import Event
from app.models.event_date import EventDate
from app.models.event_link_types import EventLinkTypes
from app.models.event_type import EventType
from app.models.space import Space
from app.models.venue_link_types import VenueLinkTypes
from app.models.venue_type import VenueType
from app.models.venue import Venue
from app.models.genre_link_types import GenreLinkTypes
from app.models.genre_type import GenreType
from app.models.space_type import SpaceType

from app.models.event_date_link_images import EventDateLinkImages
from app.models.event_link_images import EventLinkImages
from app.models.image import Image

from app.models.user_role import UserRole

from app.enum.sort_order import SortOrder
from app.core.parser import parse_date


async def get_events_by_filter(db: AsyncSession, filters: dict, base_url: str, lang: str = 'de'):
    filtered_i18n = (
        select(I18nLocale.id, I18nLocale.iso_639_1)
        .where(I18nLocale.iso_639_1 == lang)
        .cte('FilteredI18n')
    )

    venue_types = (
        select(VenueType.type_id.label('venue_type_id'),
               VenueType.name.label('venue_name'), filtered_i18n.c.iso_639_1)
        .join(filtered_i18n, filtered_i18n.c.id == VenueType.i18n_locale_id)
        .cte('VenueTypes')
    )

    event_types = (
        select(EventType.type_id.label('event_type_id'),
               EventType.name.label('event_name'), filtered_i18n.c.iso_639_1)
        .join(filtered_i18n, filtered_i18n.c.id == EventType.i18n_locale_id)
        .cte('EventTypes')
    )

    genre_types = (
        select(GenreType.type_id.label('genre_type_id'),
               GenreType.name.label('genre_name'), filtered_i18n.c.iso_639_1)
        .join(filtered_i18n, filtered_i18n.c.id == GenreType.i18n_locale_id)
        .cte('GenreTypes')
    )

    space_types = (
        select(SpaceType.type_id.label('space_type_id'),
               SpaceType.name.label('space_type'))
        .join(filtered_i18n, filtered_i18n.c.id == SpaceType.i18n_locale_id)
        .cte('SpaceTypes')
    )

    # Aliases
    cet = aliased(event_types)
    get = aliased(genre_types)
    gvt = aliased(venue_types)
    spt = aliased(space_types)

    stmt = (
        select(
            Event.id.label('event_id'),
            EventDate.id.label('event_date_id'),
            Venue.id.label('venue_id'),
            Venue.name.label('venue_name'),
            Venue.postal_code.label('venue_postcode'),
            Venue.city.label('venue_city'),
            Event.title.label('event_title'),
            Event.description.label('event_description'),
            EventDate.date_start.label('event_date_start'),
            Event.created_at.label('event_created_at'),
            func.string_agg(func.distinct(cet.c.event_name),
                            ', ').label('event_type'),
            func.string_agg(func.distinct(get.c.genre_name),
                            ', ').label('genre_type'),
            Organizer.name.label('organizer_name'),
            Space.name.label('space_name'),
            spt.c.space_type,
            func.string_agg(func.distinct(gvt.c.venue_name),
                            ', ').label('venue_type'),
            func.nullif(
                func.concat(base_url, 'uploads/', Image.source_name),
                base_url + 'uploads/').label('image_url'),
            cast(ST_AsGeoJSON(Venue.wkb_geometry, 15), JSON).label('geojson')

        )
        .select_from(Event)
        .join(EventDate, Event.id == EventDate.event_id)
        .outerjoin(Venue, Venue.id == func.coalesce(
            EventDate.venue_id, Event.venue_id)
        )
        .outerjoin(Space, Space.id == func.coalesce(
            EventDate.space_id, Event.space_id)
        )
        .outerjoin(
            EventLinkTypes,
            EventLinkTypes.event_id == Event.id
        )
        .outerjoin(EventType, EventType.id == EventLinkTypes.event_type_id)
        .outerjoin(cet, cet.c.event_type_id == EventLinkTypes.event_type_id)
        .outerjoin(GenreLinkTypes, GenreLinkTypes.event_id == Event.id)
        .outerjoin(GenreType, GenreType.id == GenreLinkTypes.genre_type_id)
        .outerjoin(get, get.c.genre_type_id == GenreLinkTypes.genre_type_id)
        .outerjoin(
            VenueLinkTypes,
            VenueLinkTypes.venue_id == Venue.id
        )
        .outerjoin(gvt, gvt.c.venue_type_id == VenueLinkTypes.venue_type_id)
        .outerjoin(spt, spt.c.space_type_id == Space.space_type_id)
        .outerjoin(Organizer, Organizer.id == Event.organizer_id)
        .outerjoin(
            EventDateLinkImages,
            (EventDateLinkImages.event_date_id == EventDate.id) &
            (EventDateLinkImages.main_image)
        )
        .outerjoin(
            EventLinkImages,
            (EventLinkImages.event_id == Event.id) &
            (EventLinkImages.main_image)
        )
        .outerjoin(
            Image,
            Image.id == func.coalesce(
                EventDateLinkImages.image_id, EventLinkImages.image_id))
        .group_by(
            Event.id,
            EventDate.id,
            Venue.id,
            Event.title,
            Event.description,
            Organizer.name,
            Venue.name,
            Venue.postal_code,
            Venue.city,
            EventDate.date_start,
            Event.created_at,
            Space.name,
            spt.c.space_type,
            Image.source_name
        )
        .order_by(EventDate.date_start)
    )

    # Dictionary to group values by column name
    column_filters = {}

    # Apply multiple filters dynamically
    for column_name, filter_value in filters.items():
        if column_name in ['date_start', 'date_end']:
            parsed_date, date_operator = parse_date(filter_value)

            if date_operator == '=':
                stmt = stmt.where(EventDate.date_start == parsed_date)
            elif date_operator == '>':
                stmt = stmt.where(EventDate.date_start > parsed_date)
            elif date_operator == '<':
                stmt = stmt.where(EventDate.date_start < parsed_date)
            elif date_operator == '>=':
                stmt = stmt.where(EventDate.date_start >= parsed_date)
            elif date_operator == '<=':
                stmt = stmt.where(EventDate.date_start <= parsed_date)
            else:
                raise ValueError(f'Invalid operator: {date_operator}')

        elif column_name in ['city', 'postal_code']:
            column_attr = getattr(Venue, column_name)
            stmt = stmt.where(column_attr == filter_value)

        elif column_name == 'venue_id':
            column_attr = Venue.id
            column_filters.setdefault(column_attr, []).extend(filter_value)

        elif column_name == 'event_type_id':
            column_attr = cet.c.event_type_id
            column_filters.setdefault(column_attr, []).extend(filter_value)

        elif column_name == 'venue_type_id':
            column_attr = gvt.c.venue_type_id
            column_filters.setdefault(column_attr, []).extend(filter_value)

        elif column_name == 'genre_type_id':
            column_attr = get.c.genre_type_id
            column_filters.setdefault(column_attr, []).extend(filter_value)

        elif column_name in ['id', 'space_id']:
            column_attr = getattr(Event, column_name)
            column_filters.setdefault(column_attr, []).extend(filter_value)

    # Apply OR conditions for grouped filters
    for column_attr, values in column_filters.items():
        stmt = stmt.where(or_(*[column_attr == value for value in values]))

    result = await db.execute(stmt)
    events = result.mappings().all()

    return events


async def get_events_sort_by(db: AsyncSession, order: dict, base_url: str, lang: str = 'de'):
    order_function = asc if order == SortOrder.asc else desc

    filtered_i18n = (
        select(I18nLocale.id, I18nLocale.iso_639_1)
        .where(I18nLocale.iso_639_1 == lang)
        .cte('FilteredI18n')
    )

    venue_types = (
        select(VenueType.type_id.label('venue_type_id'),
               VenueType.name.label('venue_name'), filtered_i18n.c.iso_639_1)
        .join(filtered_i18n, filtered_i18n.c.id == VenueType.i18n_locale_id)
        .cte('VenueTypes')
    )

    event_types = (
        select(EventType.type_id.label('event_type_id'),
               EventType.name.label('event_name'), filtered_i18n.c.iso_639_1)
        .join(filtered_i18n, filtered_i18n.c.id == EventType.i18n_locale_id)
        .cte('EventTypes')
    )

    genre_types = (
        select(GenreType.type_id.label('genre_type_id'),
               GenreType.name.label('genre_name'), filtered_i18n.c.iso_639_1)
        .join(filtered_i18n, filtered_i18n.c.id == GenreType.i18n_locale_id)
        .cte('GenreTypes')
    )

    space_types = (
        select(SpaceType.type_id.label('space_type_id'),
               SpaceType.name.label('space_type'))
        .join(filtered_i18n, filtered_i18n.c.id == SpaceType.i18n_locale_id)
        .cte('SpaceTypes')
    )

    # Aliases
    cet = aliased(event_types)
    get = aliased(genre_types)
    gvt = aliased(venue_types)
    spt = aliased(space_types)

    stmt = (
        select(
            Event.id.label('event_id'),
            Venue.id.label('venue_id'),
            Venue.name.label('venue_name'),
            Venue.postal_code.label('venue_postcode'),
            Venue.city.label('venue_city'),
            Event.title.label('event_title'),
            Event.description.label('event_description'),
            EventDate.date_start.label('event_date_start'),
            Event.created_at.label('event_created_at'),
            func.string_agg(func.distinct(cet.c.event_name),
                            ', ').label('event_type'),
            func.string_agg(func.distinct(get.c.genre_name),
                            ', ').label('genre_type'),
            Organizer.name.label('organizer_name'),
            Space.name.label('space_name'),
            spt.c.space_type,
            func.string_agg(func.distinct(gvt.c.venue_name),
                            ', ').label('venue_type'),
            func.nullif(func.concat(base_url, 'uploads/', Image.source_name),
                        base_url + 'uploads/').label('image_url')
        )
        .select_from(Event)
        .join(EventDate, Event.id == EventDate.event_id)
        .join(Venue, Venue.id == func.coalesce(EventDate.venue_id, Event.venue_id), isouter=True)
        .join(Space, Space.id == func.coalesce(EventDate.space_id, Event.space_id), isouter=True)
        .join(EventLinkTypes, EventLinkTypes.event_id == Event.id, isouter=True)
        .outerjoin(EventType, EventType.id == EventLinkTypes.event_type_id)
        .outerjoin(cet, cet.c.event_type_id == EventLinkTypes.event_type_id)
        .outerjoin(GenreLinkTypes, GenreLinkTypes.event_id == Event.id)
        .outerjoin(GenreType, GenreType.id == GenreLinkTypes.genre_type_id)
        .outerjoin(get, get.c.genre_type_id == GenreLinkTypes.genre_type_id)
        .outerjoin(VenueLinkTypes, VenueLinkTypes.venue_id == Venue.id)
        .outerjoin(gvt, gvt.c.venue_type_id == VenueLinkTypes.venue_type_id)
        .outerjoin(spt, spt.c.space_type_id == Space.space_type_id)
        .outerjoin(Organizer, Organizer.id == Event.organizer_id)
        .outerjoin(EventDateLinkImages, (EventDateLinkImages.event_date_id == EventDate.id) & (EventDateLinkImages.main_image == True))
        .outerjoin(EventLinkImages, (EventLinkImages.event_id == Event.id) & (EventLinkImages.main_image == True))
        .outerjoin(Image, Image.id == func.coalesce(EventDateLinkImages.image_id, EventLinkImages.image_id))
        .group_by(
            Event.id,
            Venue.id,
            Event.title,
            Event.description,
            Organizer.name,
            Venue.name,
            Venue.postal_code,
            Venue.city,
            EventDate.date_start,
            Event.created_at,
            Space.name,
            spt.c.space_type,
            Image.source_name
        )
        .order_by(order_function(Event.created_at))
    )

    result = await db.execute(stmt)
    events = result.mappings().all()

    return events


async def add_event_image(db: AsyncSession, image: ImageCreate):
    new_image = Image(
        user_id=image.image_user_id,
        origin_name=image.image_origin_name,
        mime_type=image.image_mime_type,
        license_type_id=image.image_license_type_id,
        copyright=image.image_copyright,
        image_type_id=image.image_type_id,
        alt_text=image.image_alt_text,
        caption=image.image_caption,
        source_name=image.image_source_name,
        width=image.image_width,
        height=image.image_height
    )

    db.add(new_image)

    try:
        await db.commit()
        await db.refresh(new_image)

        return new_image
    except IntegrityError:
        await db.rollback()


async def add_event_link_image(db: AsyncSession, event_id: int, image_id: int):
    new_event = EventLinkImages(
        event_id=event_id,
        image_id=image_id,
        main_image=True
    )

    db.add(new_event)

    try:
        await db.commit()
        await db.refresh(new_event)

        return new_event
    except IntegrityError:
        await db.rollback()


async def add_event_link_type(db: AsyncSession, event_id: int, type_id: int):
    new_event_type_link = EventLinkTypes(
        event_id=event_id,
        event_type_id=type_id
    )

    db.add(new_event_type_link)

    try:
        await db.commit()
        await db.refresh(new_event_type_link)
        return new_event_type_link
    except IntegrityError as e:
        await db.rollback()

        error_message = str(e.orig)
        match = re.search(r'\(([a-zA-Z\_]+)\)=\((-?\d+)\)', error_message)

        if match:
            column_name = match.group(1)
            column_value = match.group(2)

            if column_name in ['event_type_id', 'event_id']:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'The {column_name} ({column_value}) provided is invalid.'
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Foreign key constraint violation.'
            )


async def add_event(db: AsyncSession, event: EventCreate):
    new_event = Event(
        title=event.event_title,
        description=event.event_description,
        organizer_id=event.event_organizer_id,
        venue_id=event.event_venue_id,
        space_id=event.event_space_id
    )

    db.add(new_event)

    try:
        await db.commit()
        await db.refresh(new_event)

        return new_event
    except IntegrityError as e:
        await db.rollback()

        error_message = str(e.orig)
        match = re.search(r'\(([a-zA-Z\_]+)\)=\((-?\d+)\)', error_message)

        if match:
            column_name = match.group(1)
            column_value = match.group(2)

            if column_name in ['venue_id', 'space_id', 'organizer_id']:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'The {column_name} ({column_value}) provided is invalid.'
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Foreign key constraint violation.'
            )


async def get_events_by_user_id(db: AsyncSession, user_id: int):
    stmt = (
        select(
            Event.id.label('event_id'),
            EventDate.id.label('event_date_id'),
            Event.title.label('event_title'),
            Venue.name.label('event_venue_name'),
            func.min(EventDate.date_start).label('event_date_start_first'),
            func.max(EventDate.date_start).label('event_date_start_last'),
            case((
                UserRole.event & exists(
                    select(1)
                    .where(
                        UserOrganizerLinks.user_id == user_id
                    )
                    .where(
                        UserOrganizerLinks.organizer_id == Event.organizer_id
                    )
                    .correlate(Event, Organizer)
                ),
                True
            ), else_=False
            ).label('can_edit')
        )
        .join(Venue, Venue.id == Event.venue_id)
        .join(EventDate, EventDate.event_id == Event.id)
        .join(Organizer, Organizer.id == Event.organizer_id)
        .join(UserOrganizerLinks, UserOrganizerLinks.organizer_id == Organizer.id)
        .join(UserRole, UserRole.id == UserOrganizerLinks.user_role_id)
        .where(UserOrganizerLinks.user_id == user_id)
        .where(EventDate.date_start >= func.now())
        .group_by(
            Event.id, EventDate.id, Venue.id, Venue.name, UserRole.event
        )
        .order_by(EventDate.date_start, Event.title, Event.id)
    )

    result = await db.execute(stmt)
    events = result.mappings().all()

    return events


async def get_simple_event_by_id(db: AsyncSession, event_id: int):
    stmt = (
        select(Event).where(Event.id == event_id)
    )

    result = await db.execute(stmt)
    event = result.scalars().first()

    return event


async def get_simple_event_date_by_id(db: AsyncSession, event_date_id: int):
    stmt = (
        select(EventDate).where(EventDate.id == event_date_id)
    )

    result = await db.execute(stmt)
    event = result.scalars().first()

    return event


async def update_event_by_id(db: AsyncSession, event: EventUpdate):
    stmt = Event(
        title=event.event_title,
        description=event.event_description,
        organizer_id=event.event_organizer_id,
        venue_id=event.event_venue_id,
        space_id=event.event_space_id
    )

    try:
        await db.commit(stmt)
        await db.refresh(stmt)

        return stmt
    except IntegrityError as e:
        await db.rollback()

        error_message = str(e.orig)
        match = re.search(r'\(([a-zA-Z\_]+)\)=\((-?\d+)\)', error_message)

        if match:
            column_name = match.group(1)
            column_value = match.group(2)

            if column_name in ['venue_id', 'space_id', 'organizer_id']:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'The {column_name} ({column_value}) provided is invalid.'
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Foreign key constraint violation.'
            )

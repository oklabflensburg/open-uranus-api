from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.future import select
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from sqlalchemy import or_

from app.schemas.i18n_locale import I18nLocale
from app.schemas.organizer import Organizer
from app.schemas.event import Event
from app.schemas.event_date import EventDate
from app.schemas.event_link_types import EventLinkTypes
from app.schemas.event_type import EventType
from app.schemas.space import Space
from app.schemas.venue_link_types import VenueLinkTypes
from app.schemas.venue_type import VenueType
from app.schemas.venue import Venue
from app.schemas.genre_link_types import GenreLinkTypes
from app.schemas.genre_type import GenreType
from app.schemas.space_type import SpaceType

from app.core.parser import parse_date



async def get_events_by_filter(db: AsyncSession, filters: dict, lang: str = 'de'):
    filtered_i18n = (
        select(I18nLocale.id, I18nLocale.iso_639_1)
        .where(I18nLocale.iso_639_1 == lang)
        .cte('FilteredI18n')
    )

    venue_types = (
        select(VenueType, filtered_i18n.c.iso_639_1)
        .join(filtered_i18n, filtered_i18n.c.id == VenueType.i18n_locale_id)
        .cte('VenueTypes')
    )

    event_types = (
        select(EventType, filtered_i18n.c.iso_639_1)
        .join(filtered_i18n, filtered_i18n.c.id == EventType.i18n_locale_id)
        .cte('EventTypes')
    )

    genre_types = (
        select(GenreType, filtered_i18n.c.iso_639_1)
        .join(filtered_i18n, filtered_i18n.c.id == GenreType.i18n_locale_id)
        .cte('GenreTypes')
    )

    space_types = (
        select(SpaceType.type_id, SpaceType.name.label('space_type'))
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
            Event.title.label('event_title'),
            Event.description.label('event_description'),
            func.string_agg(func.distinct(cet.c.name), ', ').label('event_type'),
            func.string_agg(func.distinct(get.c.name), ', ').label('genre_type'),
            Organizer.name.label('organizer_name'),
            Venue.name.label('venue_name'),
            Venue.postal_code.label('venue_postcode'),
            Venue.city.label('venue_city'),
            EventDate.date_start.label('event_date_start'),
            Space.name.label('space_name'),
            spt.c.space_type,
            func.string_agg(func.distinct(gvt.c.name), ', ').label('venue_type')
        )
        .select_from(Event)
        .join(EventDate, Event.id == EventDate.event_id)
        .join(Venue, Venue.id == EventDate.venue_id)
        .outerjoin(Space, Space.id == EventDate.space_id)
        .outerjoin(EventLinkTypes, EventLinkTypes.event_id == Event.id)
        .outerjoin(EventType, EventType.id == EventLinkTypes.event_type_id)
        .outerjoin(cet, cet.c.type_id == EventLinkTypes.event_type_id)
        .outerjoin(GenreLinkTypes, GenreLinkTypes.event_id == Event.id)
        .outerjoin(GenreType, GenreType.id == GenreLinkTypes.genre_type_id)
        .outerjoin(get, get.c.type_id == GenreLinkTypes.genre_type_id)
        .outerjoin(VenueLinkTypes, VenueLinkTypes.venue_id == Venue.id)
        .outerjoin(gvt, gvt.c.type_id == VenueLinkTypes.venue_type_id)
        .outerjoin(spt, spt.c.type_id == Space.space_type_id)
        .outerjoin(Organizer, Organizer.id == Event.organizer_id)
        .group_by(
            Event.id,
            Event.title,
            Event.description,
            Organizer.name,
            Venue.name,
            Venue.postal_code,
            Venue.city,
            EventDate.date_start,
            Space.name,
            spt.c.space_type
        )
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

        elif column_name == 'event_type_id':
            column_attr = cet.c.type_id
            column_filters.setdefault(column_attr, []).extend(filter_value)

        elif column_name == 'venue_type_id':
            column_attr = gvt.c.type_id
            column_filters.setdefault(column_attr, []).extend(filter_value)

        elif column_name == 'genre_type_id':
            column_attr = get.c.type_id
            column_filters.setdefault(column_attr, []).extend(filter_value)

        elif column_name in ['id', 'venue_id', 'space_id']:
            column_attr = getattr(Event, column_name)
            column_filters.setdefault(column_attr, []).extend(filter_value)

    # Apply OR conditions for grouped filters
    for column_attr, values in column_filters.items():
        stmt = stmt.where(or_(*[column_attr == value for value in values]))


    result = await db.execute(stmt)
    events = result.mappings().all()

    return events

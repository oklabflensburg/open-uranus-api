from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.types import JSON
from sqlalchemy.orm import aliased
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast, or_, case, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from geoalchemy2.functions import ST_AsGeoJSON, ST_MakeEnvelope

from app.models.i18n_locale import I18nLocale
from app.models.organizer import Organizer
from app.models.user_organizer_links import UserOrganizerLinks
from app.models.venue_link_types import VenueLinkTypes
from app.models.user_venue_links import UserVenueLinks
from app.models.venue_type import VenueType
from app.models.venue import Venue
from app.models.user import User
from app.models.user_role import UserRole
from app.models.event import Event
from app.models.event_date import EventDate
from app.models.space import Space


async def get_venues_by_name_junk(db: AsyncSession, query: str):
    stmt = (
        select(
            Venue.id.label('venue_id'),
            Venue.name.label('venue_name')
        )
        .where(
            (func.lower(Venue.name).op('%')(query)) | (
                func.lower(Venue.name).ilike(f'%{query}%'))
        )
        .order_by(
            func.lower(Venue.name).ilike(f'{query}%').desc(),
            func.lower(Venue.name).ilike(f'%{query}%').desc(),
            func.similarity(func.lower(Venue.name), query).desc()
        )
        .limit(10)
    )

    venues = await db.execute(stmt)

    return venues.mappings().all()


async def get_all_venues(db: AsyncSession, lang: str = 'de'):
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

    # Aliases
    gvt = aliased(venue_types)

    stmt = (
        select(
            Venue.id.label('venue_id'),
            Venue.organizer_id.label('venue_organizer_id'),
            Organizer.name.label('venue_organizer_name'),
            Organizer.website_url.label('organizer_url'),
            Venue.name.label('venue_name'),
            Venue.street.label('venue_street'),
            Venue.house_number.label('venue_house_number'),
            Venue.postal_code.label('venue_postal_code'),
            Venue.country_code.label('venue_country_code'),
            Venue.state_code.label('venue_state_code'),
            Venue.city.label('venue_city'),
            func.string_agg(
                func.distinct(gvt.c.name), ', ').label('venue_type'),
            Venue.opened_at,
            Venue.closed_at,
            cast(ST_AsGeoJSON(Venue.wkb_geometry, 15), JSON).label('geojson')
        )
        .outerjoin(VenueLinkTypes, VenueLinkTypes.venue_id == Venue.id)
        .outerjoin(gvt, gvt.c.type_id == VenueLinkTypes.venue_type_id)
        .outerjoin(Organizer, Organizer.id == Venue.organizer_id)
        .group_by(
            Venue.id,
            Organizer.name,
            Organizer.website_url,
            Venue.name,
            Venue.street,
            Venue.house_number,
            Venue.postal_code,
            Venue.city,
            Venue.opened_at,
            Venue.closed_at,
            Venue.wkb_geometry
        ).order_by(
            func.lower(Venue.name).asc()
        )
    )

    result = await db.execute(stmt)
    venues = result.mappings().all()

    return venues


async def get_simple_venue_by_id(db: AsyncSession, venue_id: int):
    stmt = (
        select(Venue).where(Venue.id == venue_id)
    )

    result = await db.execute(stmt)
    venue = result.scalars().first()

    return venue


async def get_venue_by_id(db: AsyncSession, venue_id: int, lang: str = 'de'):
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

    # Aliases
    gvt = aliased(venue_types)

    stmt = (
        select(
            Venue.id.label('venue_id'),
            Venue.organizer_id.label('venue_organizer_id'),
            Organizer.name.label('venue_organizer_name'),
            Organizer.website_url.label('venue_organizer_url'),
            Venue.name.label('venue_name'),
            Venue.street.label('venue_street'),
            Venue.house_number.label('venue_house_number'),
            Venue.postal_code.label('venue_postal_code'),
            Venue.country_code.label('venue_country_code'),
            Venue.state_code.label('venue_state_code'),
            Venue.city.label('venue_city'),
            func.array_agg(
                func.coalesce(gvt.c.type_id, None)
            ).filter(gvt.c.type_id.isnot(None)).label('venue_type_ids'),
            Venue.opened_at.label('venue_opened_at'),
            Venue.closed_at.label('venue_closed_at'),
            cast(ST_AsGeoJSON(Venue.wkb_geometry, 15), JSON).label('geojson')
        )
        .outerjoin(VenueLinkTypes, VenueLinkTypes.venue_id == Venue.id)
        .outerjoin(gvt, gvt.c.type_id == VenueLinkTypes.venue_type_id)
        .outerjoin(Organizer, Organizer.id == Venue.organizer_id)
        .where(Venue.id == venue_id)
        .group_by(
            Venue.id,
            Organizer.name,
            Organizer.website_url,
            Venue.name,
            Venue.street,
            Venue.house_number,
            Venue.postal_code,
            Venue.city,
            Venue.opened_at,
            Venue.closed_at,
            Venue.wkb_geometry
        )
    )

    result = await db.execute(stmt)
    venues = result.mappings().first()

    return venues


async def get_venues_within_bounds(
    db: AsyncSession,
    xmin: float,
    ymin: float,
    xmax: float,
    ymax: float
):
    stmt = (
        select(
            Venue.id,
            Venue.name,
            ST_AsGeoJSON(Venue.wkb_geometry).label('geojson')
        )
        .where(
            Venue.wkb_geometry.ST_Within(
                ST_MakeEnvelope(xmin, ymin, xmax, ymax, 4326))
        )
    )

    venues = await db.execute(stmt)

    return venues.mappings().all()


async def get_venues_by_user_id(db: AsyncSession, user_id: int):
    uol2 = aliased(UserOrganizerLinks)
    uvl = aliased(UserVenueLinks)

    stmt = (
        select(
            Venue.id.label('venue_id'),
            Venue.organizer_id.label('venue_organizer_id'),
            Venue.name.label('venue_name'),
            case(
                (
                    UserRole.venue & exists(
                        select(1)
                        .where(uol2.user_id == user_id)
                        .where(uol2.organizer_id == Venue.organizer_id)
                        .correlate(Venue)
                    ),
                    True,
                ),
                (
                    exists(
                        select(1)
                        .where(uvl.user_id == user_id)
                        .where(uvl.venue_id == Venue.id)
                        .correlate(Venue)
                    ),
                    True,
                ),
                else_=False,
            ).label('can_edit_venue'),
            case(
                (
                    UserRole.space & exists(
                        select(1)
                        .where(uol2.user_id == user_id)
                        .where(uol2.organizer_id == Venue.organizer_id)
                        .correlate(Venue)
                    ),
                    True,
                ),
                else_=False,
            ).label('can_edit_space'),
            case(
                (
                    UserRole.event & exists(
                        select(1)
                        .where(uol2.user_id == user_id)
                        .where(uol2.organizer_id == Venue.organizer_id)
                        .correlate(Venue)
                    ),
                    True,
                ),
                else_=False,
            ).label('can_edit_event'),
        )
        .join(Organizer, Organizer.id == Venue.organizer_id)
        .join(UserOrganizerLinks, UserOrganizerLinks.organizer_id == Organizer.id)
        .join(UserRole, UserRole.id == UserOrganizerLinks.user_role_id)
        .where(UserOrganizerLinks.user_id == user_id)
        .order_by(Venue.name)
    )

    result = await db.execute(stmt)
    venues = result.mappings().all()

    return venues


async def add_venue(db: AsyncSession, new_venue: Venue):
    db.add(new_venue)

    await db.commit()
    await db.refresh(new_venue)

    return new_venue


async def add_user_venue(db: AsyncSession, user_id: int, venue_id: int):
    new_user_venue = UserVenueLinks(
        user_id=user_id,
        venue_id=venue_id
    )

    db.add(new_user_venue)

    try:
        await db.commit()
        await db.refresh(new_user_venue)

        return new_user_venue
    except IntegrityError:
        await db.rollback()


async def get_venue_stats(db: AsyncSession, venue_id: int):
    stmt = (
        select(
            func.count(Space.id.distinct()).label('count_spaces'),
            func.count(Event.id.distinct()).label('count_events')
        )
        .select_from(Venue)
        .join(Space, Space.venue_id == Venue.id)
        .outerjoin(Event, Event.venue_id == Venue.id)
        .outerjoin(
            EventDate, (EventDate.event_id == Event.id) &
            (EventDate.date_start >= datetime.now())
        )
        .where(Venue.id == venue_id)
    )

    result = await db.execute(stmt)
    stats = result.mappings().first()

    return stats


async def add_venue_link_type(
    db: AsyncSession,
    venue_id: int,
    venue_type_id: int
):
    new_link_type = VenueLinkTypes(
        venue_id=venue_id,
        venue_type_id=venue_type_id
    )

    db.add(new_link_type)

    await db.commit()
    await db.refresh(new_link_type)

    return new_link_type

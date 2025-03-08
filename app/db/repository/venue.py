from sqlalchemy.sql import func
from sqlalchemy.types import JSON
from sqlalchemy.orm import aliased
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast
from sqlalchemy.ext.asyncio import AsyncSession

from geoalchemy2.functions import ST_AsGeoJSON, ST_MakeEnvelope

from app.models.i18n_locale import I18nLocale
from app.models.organizer import Organizer
from app.models.venue_link_types import VenueLinkTypes
from app.models.venue_type import VenueType
from app.models.venue import Venue



async def get_venues_by_name_junk(db: AsyncSession, query: str):
    stmt = (
        select(
            Venue.id.label('venue_id'),
            Venue.name.label('venue_name')
        )
        .where(
            (func.lower(Venue.name).op('%')(query)) | (func.lower(Venue.name).ilike(f'%{query}%'))
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
            Organizer.name.label('organizer_name'),
            Organizer.website_url.label('organizer_url'),
            Venue.name.label('venue_name'),
            Venue.street.label('venue_street'),
            Venue.house_number.label('venue_house_number'),
            Venue.postal_code.label('venue_postal_code'),
            Venue.city.label('venue_city'),
            func.string_agg(func.distinct(gvt.c.name), ', ').label('venue_type'),
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
            Organizer.name.label('organizer_name'),
            Organizer.website_url.label('organizer_url'),
            Venue.name.label('venue_name'),
            Venue.street.label('venue_street'),
            Venue.house_number.label('venue_house_number'),
            Venue.postal_code.label('venue_postal_code'),
            Venue.city.label('venue_city'),
            func.string_agg(func.distinct(gvt.c.name), ', ').label('venue_type'),
            Venue.opened_at,
            Venue.closed_at,
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



async def get_venues_within_bounds(db: AsyncSession, xmin: float, ymin: float, xmax: float, ymax: float):
    stmt = (
        select(
            Venue.id,
            Venue.name,
            ST_AsGeoJSON(Venue.wkb_geometry).label('geojson')
        )
        .where(
            Venue.wkb_geometry.ST_Within(ST_MakeEnvelope(xmin, ymin, xmax, ymax, 4326))
        )
    )

    venues = await db.execute(stmt)

    return venues.mappings().all()
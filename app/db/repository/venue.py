from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.types import JSON
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast

from geoalchemy2.functions import ST_AsGeoJSON, ST_MakeEnvelope

from app.schemas.venue import Venue
from app.schemas.organizer import Organizer



async def get_all_venues(db: AsyncSession):
    stmt = (
        select(
            Venue.id.label('venue_id'),
            Organizer.name.label('organizer_name'),
            Organizer.website_url.label('organizer_url'),
            Venue.name.label('venue_name'),
            Venue.street,
            Venue.house_number,
            Venue.postal_code,
            Venue.city,
            Venue.country_code,
            Venue.opened_at,
            Venue.closed_at,
            cast(ST_AsGeoJSON(Venue.wkb_geometry, 15), JSON).label('geojson')
        )
        .outerjoin(Organizer, Organizer.id == Venue.organizer_id)
    )

    result = await db.execute(stmt)
    venues = result.all()

    return venues



async def get_venue_by_id(db: AsyncSession, venue_id: int):
    stmt = (
        select(
            Venue.id.label('venue_id'),
            Organizer.name.label('organizer_name'),
            Organizer.website_url.label('organizer_url'),
            Venue.name.label('venue_name'),
            Venue.street,
            Venue.house_number,
            Venue.postal_code,
            Venue.city,
            Venue.country_code,
            Venue.opened_at,
            Venue.closed_at,
            cast(ST_AsGeoJSON(Venue.wkb_geometry, 15), JSON).label('geojson')
        )
        .outerjoin(Organizer, Organizer.id == Venue.organizer_id)
        .where(
            Venue.id == venue_id
        )
    )

    result = await db.execute(stmt)
    venues = result.all()

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
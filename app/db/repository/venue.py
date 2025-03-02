from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql import func
from sqlalchemy.types import JSON
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast
from geoalchemy2.functions import ST_AsGeoJSON, ST_MakeEnvelope

from app.schemas.venue import Venue



async def get_all_venues(db: AsyncSession):
    stmt = select(
        *[getattr(Venue, col) for col in Venue.model_fields.keys() if col != 'wkb_geometry'],
        cast(func.ST_AsGeoJSON(Venue.wkb_geometry, 15), JSON).label('geojson')
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
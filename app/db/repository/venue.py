from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.sql import func
from sqlalchemy.types import JSON
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast

from app.schemas.venue import Venue



async def get_all_venues(db: AsyncSession):
    stmt = select(
        *[getattr(Venue, col) for col in Venue.model_fields.keys() if col != 'wkb_geometry'],
        cast(func.ST_AsGeoJSON(Venue.wkb_geometry, 15), JSON).label('wkb_geometry')
    )

    result = await db.execute(stmt)
    venues = result.all()

    return venues
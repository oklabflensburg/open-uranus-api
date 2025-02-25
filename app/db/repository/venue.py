from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.venue import Venue



async def get_all_venues(db: AsyncSession):
    result = await db.execute(select(Venue))
    
    venues = result.scalars().all()
    return venues
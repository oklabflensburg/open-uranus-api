from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.future import select

from app.schemas.event import Event



async def get_all_events(db: AsyncSession):
    result = await db.execute(select(Event))
    
    events = result.scalars().all()
    return events
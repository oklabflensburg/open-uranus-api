from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.space import Space



async def get_all_spaces(db: AsyncSession):
    result = await db.execute(select(Space))
    
    spaces = result.scalars().all()
    return spaces
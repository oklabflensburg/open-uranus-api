from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.future import select

from app.models.space import Space



async def get_all_spaces(db: AsyncSession):
    result = await db.execute(select(Space))
    
    spaces = result.scalars().all()
    return spaces



async def get_space_by_id(db: AsyncSession, space_id: int):
    stmt = (
        select(Space).where(Space.id == space_id)
    )

    result = await db.execute(stmt)
    space = result.scalars().first()

    return space



async def get_spaces_by_filter(db: AsyncSession, filters: dict):
    stmt = (select(Space))

    # Apply multiple filters dynamically
    for column_name, filter_value in filters.items():
        column = getattr(Space, column_name)

        stmt = stmt.where(column == filter_value)

    result = await db.execute(stmt)
    spaces = result.scalars().all()

    return spaces
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.future import select

from app.schemas.space import Space



async def get_all_spaces(db: AsyncSession):
    result = await db.execute(select(Space))
    
    spaces = result.scalars().all()
    return spaces



async def get_space_by_id(db: AsyncSession, space_id: int, lang: str = 'de'):
    filtered_i18n = (
        select(I18nLocale.id, I18nLocale.iso_639_1)
        .where(I18nLocale.iso_639_1 == lang)
        .cte('FilteredI18n')
    )



async def get_spaces_by_filter(db: AsyncSession, filters: dict):
    stmt = (select(Space))

    # Apply multiple filters dynamically
    for column_name, filter_value in filters.items():
        column = getattr(Space, column_name)

        stmt = stmt.where(column == filter_value)

    result = await db.execute(stmt)
    spaces = result.scalars().all()

    return spaces
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.i18n_locale import I18nLocale
from app.models.space_type import SpaceType



async def get_all_space_types(db: AsyncSession, lang: str):
    stmt = (
        select(
            SpaceType.type_id.label('space_type_id'),
            SpaceType.name.label('space_type_name'),
            SpaceType.i18n_locale_id.label('space_locale_id')
        )
    ).join(I18nLocale, I18nLocale.id == SpaceType.i18n_locale_id)

    if lang:
        stmt = stmt.where(I18nLocale.iso_639_1 == lang)

    stmt = stmt.order_by(SpaceType.name)

    result = await db.execute(stmt)
    spaces = result.mappings().all()

    return spaces

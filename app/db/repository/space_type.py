from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.i18n_locale import I18nLocale
from app.schemas.space_type import SpaceType



async def get_all_space_types(db: AsyncSession, lang: str = 'de'):
    stmt = (
        select(
            SpaceType.type_id.label('space_type_id'),
            SpaceType.name.label('space_type_name')
        )
        .join(I18nLocale, I18nLocale.id == SpaceType.i18n_locale_id)
        .where(I18nLocale.iso_639_1 == lang)
    )

    result = await db.execute(stmt)
    spaces = result.mappings().all()

    return spaces

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.i18n_locale import I18nLocale
from app.models.genre_type import GenreType



async def get_all_genre_types(db: AsyncSession, lang: str = 'de'):
    stmt = (
        select(
            GenreType.type_id.label('genre_type_id'),
            GenreType.name.label('genre_type_name')
        )
        .join(I18nLocale, I18nLocale.id == GenreType.i18n_locale_id)
        .where(I18nLocale.iso_639_1 == lang)
    )

    result = await db.execute(stmt)
    genres = result.mappings().all()

    return genres

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.i18n_locale import I18nLocale



async def get_all_i18n_locales(db: AsyncSession, lang: str = None):
    stmt = (
        select(
            I18nLocale.id.label('locale_id'),
            I18nLocale.name.label('locale_name'),
            I18nLocale.iso_639_1.label('locale_code')
        )
    )

    result = await db.execute(stmt)
    i18n_locales = result.mappings().all()

    return i18n_locales

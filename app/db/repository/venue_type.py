from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.i18n_locale import I18nLocale
from app.models.venue_type import VenueType



async def get_all_venue_types(db: AsyncSession, lang: str = 'de'):
    stmt = (
        select(
            VenueType.type_id.label('venue_type_id'),
            VenueType.name.label('venue_type_name')
        )
        .join(I18nLocale, I18nLocale.id == VenueType.i18n_locale_id)
        .where(I18nLocale.iso_639_1 == lang)
    )

    result = await db.execute(stmt)
    venues = result.mappings().all()

    return venues

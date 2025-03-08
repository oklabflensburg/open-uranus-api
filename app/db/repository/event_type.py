from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.i18n_locale import I18nLocale
from app.models.event_type import EventType



async def get_all_event_types(db: AsyncSession, lang: str = 'de'):
    stmt = (
        select(
            EventType.type_id.label('event_type_id'),
            EventType.name.label('event_type_name')
        )
        .join(I18nLocale, I18nLocale.id == EventType.i18n_locale_id)
        .where(I18nLocale.iso_639_1 == lang)
    )

    result = await db.execute(stmt)
    events = result.mappings().all()

    return events

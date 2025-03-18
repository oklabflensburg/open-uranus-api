from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.i18n_locale import I18nLocale
from app.models.event_type import EventType



async def get_all_event_types(db: AsyncSession, lang: str):
    stmt = (
        select(
            EventType.type_id.label('event_type_id'),
            EventType.name.label('event_type_name'),
            EventType.i18n_locale_id.label('event_locale_id')
        ).join(I18nLocale, I18nLocale.id == EventType.i18n_locale_id)
    )

    if lang:
        stmt = stmt.where(I18nLocale.iso_639_1 == lang)

    stmt = stmt.order_by(EventType.name)

    result = await db.execute(stmt)
    events = result.mappings().all()

    return events

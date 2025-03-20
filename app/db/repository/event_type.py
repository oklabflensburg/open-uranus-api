from sqlmodel import select
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event_link_types import EventLinkTypes
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


async def get_event_types_by_event_id(
    db: AsyncSession,
    event_id: int
):
    stmt = (
        select(EventLinkTypes)
        .join(
            EventType,
            EventType.type_id == EventLinkTypes.event_type_id
        )
        .join(
            I18nLocale,
            I18nLocale.id == EventType.i18n_locale_id
        )
        .where(EventLinkTypes.event_id == event_id)
    )

    result = await db.execute(stmt)
    event_types = result.mappings().all()

    return event_types


async def delete_event_link_type(
    db: AsyncSession,
    event_id: int,
    event_type_id: int
):
    stmt = (
        delete(EventLinkTypes)
        .where(
            EventLinkTypes.event_id == event_id,
            EventLinkTypes.event_type_id == event_type_id
        )
    )
    await db.execute(stmt)
    await db.commit()

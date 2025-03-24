import re

from fastapi import HTTPException, status

from sqlalchemy import delete
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.i18n_locale import I18nLocale
from app.models.venue_link_types import VenueLinkTypes
from app.models.venue_type import VenueType


async def get_all_venue_types(db: AsyncSession, lang: str):
    stmt = select(
        VenueType.type_id.label('venue_type_id'),
        VenueType.name.label('venue_type_name'),
        VenueType.i18n_locale_id.label('venue_locale_id')
    ).join(I18nLocale, I18nLocale.id == VenueType.i18n_locale_id
           )

    if lang:
        stmt = stmt.where(I18nLocale.iso_639_1 == lang)

    stmt = stmt.order_by(VenueType.name)

    result = await db.execute(stmt)
    venues = result.mappings().all()

    return venues


async def get_venue_types_by_venue_id(
    db: AsyncSession,
    venue_id: int
):
    stmt = (
        select(VenueLinkTypes)
        .join(
            VenueType,
            VenueType.type_id == VenueLinkTypes.venue_type_id
        )
        .join(
            I18nLocale,
            I18nLocale.id == VenueType.i18n_locale_id
        )
        .where(VenueLinkTypes.venue_id == venue_id)
    )

    result = await db.execute(stmt)
    venue_types = result.mappings().all()

    return venue_types


async def delete_venue_link_type(
    db: AsyncSession,
    venue_id: int,
    venue_type_id: int
):
    stmt = (
        delete(VenueLinkTypes)
        .where(
            VenueLinkTypes.venue_id == venue_id,
            VenueLinkTypes.venue_type_id == venue_type_id
        )
    )
    await db.execute(stmt)
    await db.commit()


async def add_venue_link_type(db: AsyncSession, venue_id: int, type_id: int):
    new_venue_type_link = VenueLinkTypes(
        venue_id=venue_id,
        venue_type_id=type_id
    )

    db.add(new_venue_type_link)

    try:
        await db.commit()
        await db.refresh(new_venue_type_link)
        return new_venue_type_link
    except IntegrityError as e:
        await db.rollback()

        error_message = str(e.orig)
        match = re.search(r'\(([a-zA-Z\_]+)\)=\((-?\d+)\)', error_message)

        if match:
            column_name = match.group(1)
            column_value = match.group(2)

            if column_name in ['venue_type_id', 'venue_id']:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'The {column_name} ({column_value}) provided is invalid.'
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Foreign key constraint violation.'
            )

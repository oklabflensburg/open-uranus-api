from sqlmodel import select
from sqlalchemy.sql.expression import distinct, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import re

from app.models.i18n_locale import I18nLocale
from app.models.genre_type import GenreType
from app.models.genre_link_types import GenreLinkTypes


async def get_all_genre_types(db: AsyncSession, lang: str):
    stmt = (
        select(
            GenreType.type_id.label('genre_type_id'),
            GenreType.name.label('genre_type_name'),
            GenreType.i18n_locale_id.label('genre_locale_id')
        ).join(I18nLocale, I18nLocale.id == GenreType.i18n_locale_id)
    )

    if lang:
        stmt = stmt.where(I18nLocale.iso_639_1 == lang)

    stmt = stmt.order_by(GenreType.name)

    result = await db.execute(stmt)
    genres = result.mappings().all()

    return genres


async def add_genre_link_type(
    db: AsyncSession,
    event_id: int,
    genre_type_id: int
):
    new_genre_type_link = GenreLinkTypes(
        event_id=event_id,
        genre_type_id=genre_type_id
    )

    db.add(new_genre_type_link)

    try:
        await db.commit()
        await db.refresh(new_genre_type_link)

        return new_genre_type_link
    except IntegrityError as e:
        await db.rollback()

        error_message = str(e.orig)

        match = re.search(r'\(([a-zA-Z\_]+)\)=\((-?\d+)\)', error_message)

        if match:
            column_name = match.group(1)
            column_value = match.group(2)

            if column_name in ['genre_type_id', 'event_id']:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'The {column_name} ({column_value}) provided is invalid.'
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Foreign key constraint violation.'
            )


async def get_genre_types_by_event_id(
    db: AsyncSession,
    event_id: int
):
    stmt = (
        select(distinct(GenreType.type_id).label('genre_type_id'))
        .join(
            GenreLinkTypes,
            GenreType.type_id == GenreLinkTypes.genre_type_id
        )
        .where(GenreLinkTypes.event_id == event_id)
    )

    result = await db.execute(stmt)
    genre_types = result.mappings().all()

    return genre_types


async def delete_genre_link_type(
    db: AsyncSession,
    event_id: int,
    genre_type_id: int
):
    stmt = (
        delete(GenreLinkTypes)
        .where(
            GenreLinkTypes.event_id == event_id,
            GenreLinkTypes.genre_type_id == genre_type_id
        )
    )
    await db.execute(stmt)
    await db.commit()

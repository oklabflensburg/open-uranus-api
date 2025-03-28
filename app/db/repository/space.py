import re

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from sqlalchemy.future import select

from app.models.space import Space

from app.schemas.space import SpaceCreate


async def get_all_spaces(db: AsyncSession):
    stmt = (
        select(
            Space.id.label('space_id'),
            Space.venue_id.label('space_venue_id'),
            Space.name.label('space_name'),
            Space.total_capacity.label('space_total_capacity'),
            Space.seating_capacity.label('space_seating_capacity'),
            Space.space_type_id.label('space_type_id'),
            Space.building_level.label('space_building_level'),
            Space.url.label('space_url')
        )
        .order_by(Space.name)
    )

    result = await db.execute(stmt)
    spaces = result.mappings().all()

    return spaces


async def get_space_by_id(db: AsyncSession, space_id: int):
    stmt = (
        select(
            Space.id.label('space_id'),
            Space.venue_id.label('space_venue_id'),
            Space.name.label('space_name'),
            Space.total_capacity.label('space_total_capacity'),
            Space.seating_capacity.label('space_seating_capacity'),
            Space.space_type_id.label('space_type_id'),
            Space.building_level.label('space_building_level'),
            Space.url.label('space_url')
        )
        .where(Space.id == space_id)
    )

    result = await db.execute(stmt)
    space = result.mappings().first()

    return space


async def get_space_by_venue_id(db: AsyncSession, venue_id: int):
    stmt = (
        select(
            Space.id.label('space_id'),
            Space.venue_id.label('space_venue_id'),
            Space.name.label('space_name'),
            Space.total_capacity.label('space_total_capacity'),
            Space.seating_capacity.label('space_seating_capacity'),
            Space.space_type_id.label('space_type_id'),
            Space.building_level.label('space_building_level'),
            Space.url.label('space_url')
        )
        .where(Space.venue_id == venue_id)
    )

    result = await db.execute(stmt)
    spaces = result.mappings().all()

    return spaces


async def add_space(db: AsyncSession, space: SpaceCreate):
    new_space = Space(
        venue_id=space.space_venue_id,
        name=space.space_name,
        total_capacity=space.space_total_capacity,
        seating_capacity=space.space_seating_capacity,
        space_type_id=space.space_type_id,
        building_level=space.space_building_level,
        url=space.space_url
    )

    db.add(new_space)

    try:
        await db.commit()
        await db.refresh(new_space)

        return new_space
    except IntegrityError as e:
        await db.rollback()

        error_message = str(e.orig)
        match = re.search(r'\(([a-zA-Z\_]+)\)=\((-?\d+)\)', error_message)

        if match:
            column_name = match.group(1)
            column_value = match.group(2)

            if column_name in ['venue_id', 'space_type_id']:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'The {column_name} ({column_value}) provided is invalid.'
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Foreign key constraint violation.'
            )


async def update_space(db: AsyncSession, space_id: int, space_data):
    stmt = (
        select(Space)
        .where(Space.id == space_id)
    )

    result = await db.execute(stmt)
    space = result.scalars().first()

    if not space:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Space with ID {space_id} not found.'
        )

    space.venue_id = space_data.space_venue_id
    space.name = space_data.space_name
    space.total_capacity = space_data.space_total_capacity
    space.seating_capacity = space_data.space_seating_capacity
    space.space_type_id = space_data.space_type_id
    space.building_level = space_data.space_building_level
    space.url = space_data.space_url

    try:
        await db.commit()
        await db.refresh(space)
        return space
    except IntegrityError as e:
        await db.rollback()

        error_message = str(e.orig)
        match = re.search(r'\(([a-zA-Z\_]+)\)=\((-?\d+)\)', error_message)

        if match:
            column_name = match.group(1)
            column_value = match.group(2)

            if column_name in ['venue_id', 'space_type_id']:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'The {column_name} ({column_value}) provided is invalid.'
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Foreign key constraint violation.'
            )

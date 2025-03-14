import re

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from sqlalchemy.future import select

from app.models.space import Space

from app.schemas.space import SpaceCreate



async def get_all_spaces(db: AsyncSession):
    result = await db.execute(select(Space))
    
    spaces = result.scalars().all()
    return spaces



async def get_space_by_id(db: AsyncSession, space_id: int):
    stmt = (
        select(Space).where(Space.id == space_id)
    )

    result = await db.execute(stmt)
    space = result.scalars().first()

    return space



async def get_spaces_by_filter(db: AsyncSession, filters: dict):
    stmt = (select(Space))

    # Apply multiple filters dynamically
    for column_name, filter_value in filters.items():
        column = getattr(Space, column_name)

        stmt = stmt.where(column == filter_value)

    result = await db.execute(stmt)
    spaces = result.scalars().all()

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
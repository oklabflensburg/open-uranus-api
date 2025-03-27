from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from app.db.session import get_db

from app.db.repository.space import (
    get_all_spaces,
    get_space_by_id,
    get_space_by_venue_id,
    add_space,
    update_space
)

from app.schemas.space import SpaceCreate, SpaceResponse
from app.models.user import User
from app.services.auth import get_current_user


router = APIRouter()


@router.get('/', response_model=List[SpaceResponse])
async def fetch_all_spaces(
    db: AsyncSession = Depends(get_db)
):
    spaces = await get_all_spaces(db)

    return spaces


@router.get('/{space_id}', response_model=SpaceResponse)
async def fetch_space_by_id(
    space_id: int,
    db: AsyncSession = Depends(get_db)
):
    space = await get_space_by_id(db, space_id)

    if space is None:
        raise HTTPException(
            status_code=404, detail=f'No space found for space_id: {space_id}')

    return space


@router.get('/venue/{venue_id}', response_model=List[SpaceResponse])
async def fetch_space_by_venue_id(
    venue_id: int,
    db: AsyncSession = Depends(get_db)
):
    spaces = await get_space_by_venue_id(db, venue_id)

    if len(spaces) == 0:
        raise HTTPException(
            status_code=404, detail=f'No spaces found for venue_id: {venue_id}')

    return spaces


@router.post('/', response_model=SpaceResponse)
async def create_space(
    space_data: SpaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_space = await add_space(db, space_data)

    return SpaceResponse(
        space_id=new_space.id,
        space_venue_id=new_space.venue_id,
        space_name=new_space.name,
        space_total_capacity=new_space.total_capacity,
        space_seating_capacity=new_space.seating_capacity,
        space_type_id=new_space.space_type_id,
        space_building_level=new_space.building_level,
        space_url=new_space.url
    )


@router.put('/{space_id}', response_model=SpaceResponse)
async def update_space_by_id(
    space_id: int,
    space_data: SpaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    space = await get_space_by_id(db, space_id)
    if space is None:
        raise HTTPException(
            status_code=404, detail=f'No space found for space_id: {space_id}')

    updated_space = await update_space(db, space_id, space_data)

    return SpaceResponse(
        space_id=updated_space.id,
        space_venue_id=updated_space.venue_id,
        space_name=updated_space.name,
        space_total_capacity=updated_space.total_capacity,
        space_seating_capacity=updated_space.seating_capacity,
        space_type_id=updated_space.space_type_id,
        space_building_level=updated_space.building_level,
        space_url=updated_space.url
    )

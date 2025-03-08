from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from typing import List, Optional

from app.models.space import Space

from app.db.repository.space import get_all_spaces, get_spaces_by_filter, get_space_by_id




router = APIRouter()

@router.get('/', response_model=List[Space])
async def fetch_all_spaces(
    db: AsyncSession = Depends(get_db)
):
    spaces = await get_all_spaces(db)

    return spaces



@router.get('/id', response_model=Space)
async def fetch_space_by_id(
    space_id: int,
    db: AsyncSession = Depends(get_db)
):
    space = await get_space_by_id(db, space_id)

    if space is None:
        raise HTTPException(status_code=404, detail=f'No space found for space_id: {space_id}')

    return space



@router.get('/filtered', response_model=List[Space])
async def fetch_spaces_by_filter(
    space_id: Optional[int] = Query(None),
    venue_id: Optional[int] = Query(None),
    space_type_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    filters = {
        'id': space_id,
        'venue_id': venue_id,
        'space_type_id': space_type_id
    }

    # Remove filters with None values
    active_filters = {key: value for key, value in filters.items() if value not in [None, '']}

    if not active_filters:
        raise HTTPException(status_code=400, detail='At least one filter parameter is required')


    spaces = await get_spaces_by_filter(db, active_filters)

    return spaces

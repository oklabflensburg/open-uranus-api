from app.schemas.state import StateResponse
from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.db.repository.state import (
    get_all_states,
    get_state_by_name,
    get_state_by_code
)

from typing import List


router = APIRouter()


@router.get('/', response_model=List[StateResponse])
async def fetch_all_states(
    db: AsyncSession = Depends(get_db)
):
    states = await get_all_states(db)

    return states


@router.get('/name', response_model=StateResponse)
async def fetch_state_by_name(
    state_name: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    state = await get_state_by_name(db, state_name)

    return state


@router.get('/code', response_model=StateResponse)
async def fetch_state_by_code(
    state_code: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    state = await get_state_by_code(db, state_code)

    return state

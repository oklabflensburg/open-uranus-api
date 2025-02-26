from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.db.repository.event import get_all_events, get_all_detailed_events

from app.schemas.event import Event
from app.schemas.event_response import EventResponse


router = APIRouter()

@router.get('/', response_model=List[Event])
async def fetch_all_events(db: AsyncSession = Depends(get_db)):
    events = await get_all_events(db)

    return events



@router.get('/detailed', response_model=List[EventResponse])
async def fetch_all_detailed_events(
    city: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    events = await get_all_detailed_events(db, city)

    return events

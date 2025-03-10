from fastapi import APIRouter, HTTPException, Request, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from sqlmodel import select

from app.db.session import get_db
from app.db.repository.event import get_events_by_filter, get_events_sort_by

from app.models.event import Event
from app.schemas.event_response import EventResponse

from app.enum.sort_order import SortOrder



router = APIRouter()


@router.get('/', response_model=List[EventResponse])
async def fetch_events_by_filter(
    request: Request,
    city: Optional[str] = Query(None),
    postal_code: Optional[str] = Query(None),
    venue_id: Optional[List[int]] = Query(None),
    event_id: Optional[List[int]] = Query(None),
    space_id: Optional[List[int]] = Query(None),
    event_type_id: Optional[List[int]] = Query(None),
    venue_type_id: Optional[List[int]] = Query(None),
    genre_type_id: Optional[List[int]] = Query(None),
    date_start: Optional[str] = Query(None),
    date_end: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    filters = {
        'city': city,
        'postal_code': postal_code,
        'id': event_id,
        'venue_id': venue_id,
        'space_id': space_id,
        'event_type_id': event_type_id,
        'venue_type_id': venue_type_id,
        'genre_type_id': genre_type_id,
        'date_start': date_start,
        'date_end': date_end
    }

    # Remove filters with None values
    active_filters = {key: value for key, value in filters.items() if value not in [None, '']}

    if not active_filters:
        raise HTTPException(status_code=400, detail='At least one filter parameter is required')

    base_url = str(request.base_url)
    events = await get_events_by_filter(db, active_filters, base_url)

    if len(events) < 1:
        raise HTTPException(status_code=404, detail=f'No events found for filters: {active_filters}')

    return events





@router.get('/sort', response_model=List[EventResponse])
async def fetch_events_sort_by(
    request: Request,
    order_by: SortOrder = SortOrder.asc,
    db: AsyncSession = Depends(get_db)
):
    base_url = str(request.base_url)
    events = await get_events_sort_by(db, order_by, base_url)

    if len(events) < 1:
        raise HTTPException(status_code=404, detail=f'No events found for filters: {active_filters}')

    return events

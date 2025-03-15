from fastapi import APIRouter, HTTPException, Request, Depends, Query, status, UploadFile, File

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

import uuid
import shutil
import os

from app.core.config import settings
from app.db.session import get_db
from app.db.repository.event import get_events_by_filter, get_events_sort_by, get_simple_event_by_id, add_event
from app.db.repository.event_date import add_event_date
from app.models.image import Image

from app.models.user import User

from app.schemas.event import EventCreate, EventResponse, EventQueryResponse

from app.enum.sort_order import SortOrder

from app.services.auth import get_current_user
from app.services.validators import validate_image


router = APIRouter()


@router.get('/', response_model=List[EventQueryResponse])
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



@router.post('/', response_model=EventResponse)
async def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_event = await add_event(db, event_data)
    new_event_date = await add_event_date(db, event_data, new_event)

    return EventResponse(
        event_id=new_event.id,
        event_title=new_event.title,
        event_description=new_event.description,
        event_organizer_id=new_event.organizer_id,
        event_venue_id=new_event.venue_id,
        event_space_id=new_event.space_id,
        event_date_start=new_event_date.date_start,
        event_date_end=new_event_date.date_end
    )


@router.post('/upload')
async def upload_event_image(
    file: UploadFile = File(...),
    ext: str = Depends(validate_image),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    source_name = f'{uuid.uuid4()}.{ext}'
    file_path = os.path.join(settings.UPLOAD_DIR, source_name)

    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_image = Image(
        source_name=source_name,
        license_type_id=1,
        origin_name='tbd',
        mime_type='is nen image',
        image_type_id=1
    )

    db.add(new_image)

    await db.commit()
    await db.refresh(new_image)

    return {'source_name': source_name}



@router.delete('/{event_id}', response_model=dict)
async def delete_event_by_id(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    venue = await get_simple_event_by_id(db, event_id)

    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No venue found for event_id: {event_id}'
        )

    await db.delete(venue)
    await db.commit()

    return {'message': 'Venue deleted successfully'}



@router.get('/sort', response_model=List[EventQueryResponse])
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

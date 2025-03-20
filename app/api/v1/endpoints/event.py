import re

from datetime import datetime, time

from fastapi import APIRouter, HTTPException, Request, Depends, Query, status, UploadFile, File, Form

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import Optional, List

import uuid
import shutil
import os
import mimetypes

from PIL import Image as PILImage

from app.core.config import settings
from app.db.session import get_db

from app.db.repository.event import (
    add_event_image,
    add_event_link_image,
    add_event_link_type,
    get_events_by_filter,
    get_events_sort_by,
    get_simple_event_by_id,
    get_simple_event_date_by_id,
    add_event
)

from app.db.repository.event_date import (
    add_event_date,
    get_event_by_event_date_id
)

from app.db.repository.event_type import (
    get_event_types_by_event_id,
    delete_event_link_type
)

from app.db.repository.image import (
    get_main_image_id_by_event_id
)

from app.models.image import Image

from app.models.user import User

from app.schemas.image import ImageCreate
from app.schemas.event import EventCreate, EventResponse, EventQueryResponse
from app.schemas.event_date import EventDateResponse

from app.enum.sort_order import SortOrder

from app.services.auth import get_current_user
from app.services.validators import validate_image


router = APIRouter()

MAX_IMAGE_PX_SIZE = 2000


@router.get('/{event_date_id}', response_model=EventDateResponse)
async def fetch_event_by_event_date_id(
    request: Request,
    lang: str,
    event_date_id: int,
    db: AsyncSession = Depends(get_db)
):
    base_url = str(request.base_url)

    event = await get_event_by_event_date_id(db, base_url, event_date_id, lang)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f'No event date found for event_date_id: {event_date_id}'
            )
        )

    return event


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
    active_filters = {key: value for key, value in filters.items() if value not in [
        None, '']}

    if not active_filters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='At least one filter parameter is required')

    base_url = str(request.base_url)
    events = await get_events_by_filter(db, active_filters, base_url)

    if len(events) < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No events found for filters: {active_filters}'
        )

    return events


@router.put('/{event_date_id}', response_model=EventResponse)
async def update_event_by_event_date_id(
    event_date_id: int,
    event_title: str = Form(...),
    event_description: str = Form(...),
    event_organizer_id: int = Form(...),
    event_venue_id: int = Form(...),
    event_type_id: List[int] = Form(...),
    event_space_id: Optional[int] = Form(None),
    event_image_type_id: Optional[int] = Form(None),
    event_image_license_type_id: Optional[int] = Form(None),
    event_date_start: datetime = Form(...),
    event_date_end: Optional[datetime] = Form(None),
    event_entry_time: Optional[time] = Form(None),
    event_image_alt: Optional[str] = Form(None),
    event_image_caption: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    ext: Optional[str] = Depends(validate_image),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    event_date = await get_simple_event_date_by_id(db, event_date_id)

    if not event_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No event date found for event_date_id: {event_date_id}'
        )

    if event_date_start:
        event_date.date_start = event_date_start.replace(tzinfo=None)

    if event_date_end:
        event_date.date_end = event_date_end.replace(tzinfo=None)

    if event_entry_time:
        event_date.entry_time = event_entry_time

    event_date.venue_id = event_venue_id
    event_date.space_id = event_space_id

    try:
        await db.commit()
        await db.refresh(event_date)
    except IntegrityError as e:
        await db.rollback()

        error_message = str(e.orig)
        match = re.search(r'\(([a-zA-Z_]+)\)=\((-?\d+)\)', error_message)

        if match:
            column_name = match.group(1)
            column_value = match.group(2)

            if column_name in ['venue_id', 'space_id']:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'The {column_name} ({column_value}) provided is invalid.',
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Foreign key constraint violation.',
            )

    event = await get_simple_event_by_id(db, event_date.event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No event found for event_id: {event_date.event_id}'
        )

    event.title = event_title
    event.description = event_description

    try:
        await db.commit()
        await db.refresh(event)
    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Foreign key constraint violation.',
        )

    if file:
        image = await get_main_image_id_by_event_id(db, event_date.event_id)

        print(image)
        source_name = f'{uuid.uuid4()}.{ext}'
        file_path = os.path.join(settings.UPLOAD_DIR, source_name)

        with open(file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)

        mime_type, _ = mimetypes.guess_type(file_path)

        with PILImage.open(file_path) as img:
            width, height = img.size

        image.origin_name = file.filename,
        image.type_id = event_image_type_id,
        image.license_type_id = event_image_license_type_id,
        image.source_name = source_name,
        image.alt_text = event_image_alt,
        image.caption = event_image_caption,
        image.mime_type = mime_type,
        image.width = width,
        image.height = height

        try:
            await db.commit()
            await db.refresh(image)
        except IntegrityError:
            await db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Foreign key constraint violation.',
            )

    current_event_types = await get_event_types_by_event_id(db, event.id)
    print(current_event_types)

    current_event_type_ids = [
        event_type['EventLinkTypes'].event_type_id for event_type in current_event_types
    ]

    ids_to_add = set(event_type_id) - set(current_event_type_ids)
    ids_to_remove = set(current_event_type_ids) - set(event_type_id)

    for type_id in ids_to_add:
        await add_event_link_type(db, event.id, type_id)

    for type_id in ids_to_remove:
        await delete_event_link_type(db, event.id, type_id)

    await db.commit()

    await get_event_types_by_event_id(db, event.id)

    return EventResponse(
        event_id=event_date.event_id,
        event_date_id=event_date_id,
        event_title=event_title,
        event_description=event_description,
        event_organizer_id=event_organizer_id,
        event_venue_id=event_venue_id,
        event_space_id=event_space_id,
        event_date_start=event_date_start,
        event_date_end=event_date_end
    )


@router.post('/', response_model=EventResponse)
async def create_event(
    event_title: str = Form(...),
    event_description: str = Form(...),
    event_organizer_id: int = Form(...),
    event_venue_id: int = Form(...),
    event_type_id: List[int] = Form(...),
    event_space_id: Optional[int] = Form(None),
    event_image_type_id: Optional[int] = Form(None),
    event_image_license_type_id: Optional[int] = Form(None),
    event_date_start: str = Form(...),
    event_date_end: Optional[str] = Form(None),
    event_image_alt: Optional[str] = Form(None),
    event_image_caption: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    ext: Optional[str] = Depends(validate_image),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if file:
        source_name = f'{uuid.uuid4()}.{ext}'
        file_path = os.path.join(settings.UPLOAD_DIR, source_name)

        with open(file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)

        mime_type, _ = mimetypes.guess_type(file_path)

        with PILImage.open(file_path) as img:
            width, height = img.size

        image_data = ImageCreate(
            image_origin_name=file.filename,
            image_type_id=event_image_type_id,
            image_license_type_id=event_image_license_type_id,
            image_source_name=source_name,
            image_alt_text=event_image_alt,
            image_caption=event_image_caption,
            image_mime_type=mime_type,
            image_width=width,
            image_height=height
        )

        new_image = await add_event_image(db, image_data)

    event_data = {
        'event_title': event_title,
        'event_description': event_description,
        'event_organizer_id': event_organizer_id,
        'event_venue_id': event_venue_id,
        'event_space_id': event_space_id,
        'event_image_type_id': event_image_type_id,
        'event_image_license_type_id': event_image_license_type_id,
        'event_date_start': event_date_start,
        'event_date_end': event_date_end
    }

    event = EventCreate(**event_data)
    new_event = await add_event(db, event)
    new_event_date = await add_event_date(db, event, new_event)

    if file:
        await add_event_link_image(db, new_event.id, new_image.id)

    for type_id in event_type_id:
        await add_event_link_type(db, new_event.id, type_id)

    return EventResponse(
        event_id=new_event.id,
        event_date_id=new_event_date.id,
        event_title=new_event.title,
        event_description=new_event.description,
        event_organizer_id=new_event.organizer_id,
        event_venue_id=new_event.venue_id,
        event_space_id=new_event.space_id,
        event_date_start=new_event_date.date_start,
        event_date_end=new_event_date.date_end
    )


@router.post('/upload', deprecated=True)
async def upload_event_image(
    file: UploadFile = File(...),
    ext: str = Depends(validate_image),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    source_name = f'{uuid.uuid4()}.{ext}'
    file_path = os.path.join(settings.UPLOAD_DIR, source_name)

    # Save the uploaded file temporarily
    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Open the image with Pillow
    with PILImage.open(file_path) as img:
        width, height = img.size

        # Check if resizing is needed
        if width > MAX_IMAGE_PX_SIZE or height > MAX_IMAGE_PX_SIZE:
            # Calculate new size while maintaining aspect ratio
            img.thumbnail((MAX_IMAGE_PX_SIZE, MAX_IMAGE_PX_SIZE),
                          PILImage.LANCZOS)
            img.save(file_path)  # Overwrite the original file

        # Get new dimensions after resizing
        new_width, new_height = img.size

    # Determine MIME type
    mime_type, _ = mimetypes.guess_type(file_path)

    # Save image metadata to database
    new_image = Image(
        source_name=source_name,
        license_type_id=1,
        origin_name=file.filename,
        mime_type=mime_type,
        image_type_id=1,
        width=new_width,
        height=new_height
    )

    db.add(new_image)
    await db.commit()
    await db.refresh(new_image)

    return {'source_name': source_name, 'width': new_width, 'height': new_height}


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No events found for order_by: {order_by}'
        )

    return events

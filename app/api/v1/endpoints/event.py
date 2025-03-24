import re

from datetime import datetime, time

from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Depends,
    Query,
    status,
    UploadFile,
    File,
    Form
)
from fastapi.responses import FileResponse
from icalendar import Calendar, Event as ICalEvent

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import Optional, List

import uuid
import shutil
import os
import mimetypes
import xml.etree.ElementTree as ET

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
    get_event_by_event_date_id,
    get_event_detail_by_event_date_id
)

from app.db.repository.event_type import (
    get_event_types_by_event_id,
    delete_event_link_type
)

from app.db.repository.image import (
    get_main_image_id_by_event_id
)

from app.models.user import User

from app.schemas.image import ImageCreate
from app.schemas.event import (
    EventCreate,
    EventResponse,
    EventQueryResponse
)

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

    active_filters = {
        key: value for key, value in filters.items()
        if value not in [None, '']
    }

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


async def process_uploaded_file(file: UploadFile, ext: str) -> dict:
    '''
    Process the uploaded file and return metadata including file path,
    dimensions, and MIME type.
    '''
    source_name = f'{uuid.uuid4()}.{ext}'
    file_path = os.path.join(settings.UPLOAD_DIR, source_name)

    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    mime_type, _ = mimetypes.guess_type(file_path)

    if ext == 'svg':
        with open(file_path, 'r') as svg_file:
            svg_content = svg_file.read()
        try:
            root = ET.fromstring(svg_content)
            width = root.attrib.get('width')
            height = root.attrib.get('height')
            width = int(float(width)) if width else None
            height = int(float(height)) if height else None
        except ET.ParseError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid SVG file format.'
            )
    else:
        with PILImage.open(file_path) as img:
            width, height = img.size

    return {
        'file_path': file_path,
        'source_name': source_name,
        'mime_type': mime_type,
        'width': width,
        'height': height
    }


def handle_integrity_error(e: IntegrityError, column_name_list: List[str]):
    '''
    Handle IntegrityError exceptions and raise
    appropriate HTTPException errors.

    :param e: The IntegrityError exception.
    :param column_name_list: List of column names
    to check for in the error message.
    '''
    error_message = str(e.orig)
    match = re.search(r'\(([a-zA-Z_]+)\)=\((-?\d+)\)', error_message)

    if match:
        column_name = match.group(1)
        column_value = match.group(2)

        if column_name in column_name_list:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'''
                    The {column_name} ({column_value}) provided is invalid.
                ''',
            )
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail='Foreign key constraint violation.',
    )


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
        handle_integrity_error(e, ['venue_id', 'space_id'])

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
    except IntegrityError as e:
        await db.rollback()
        handle_integrity_error(e, ['organizer_id', 'venue_id'])

    if file:
        image_row = await get_main_image_id_by_event_id(
            db,
            event_date.event_id
        )

        if not image_row:
            file_metadata = await process_uploaded_file(file, ext)

            new_image_data = ImageCreate(
                image_origin_name=file.filename,
                image_type_id=event_image_type_id,
                image_license_type_id=event_image_license_type_id,
                image_source_name=file_metadata['source_name'],
                image_alt_text=event_image_alt,
                image_caption=event_image_caption,
                image_mime_type=file_metadata['mime_type'],
                image_width=file_metadata['width'],
                image_height=file_metadata['height']
            )

            new_image = await add_event_image(db, new_image_data)
            await add_event_link_image(db, event_date.event_id, new_image.id)
        else:
            image = image_row['Image']

            file_metadata = await process_uploaded_file(file, ext)

            image.origin_name = file.filename
            image.image_type_id = event_image_type_id
            image.license_type_id = event_image_license_type_id
            image.source_name = file_metadata['source_name']
            image.alt_text = event_image_alt
            image.caption = event_image_caption
            image.mime_type = file_metadata['mime_type']
            image.width = file_metadata['width']
            image.height = file_metadata['height']

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
        event_type['EventLinkTypes'].event_type_id
        for event_type in current_event_types
    ]

    ids_to_add = set(event_type_id) - set(current_event_type_ids)
    ids_to_remove = set(current_event_type_ids) - set(event_type_id)

    for type_id in ids_to_add:
        await add_event_link_type(db, event.id, type_id)

    for type_id in ids_to_remove:
        await delete_event_link_type(db, event.id, type_id)

    await db.commit()

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
        file_metadata = await process_uploaded_file(file, ext)

        image_data = ImageCreate(
            image_origin_name=file.filename,
            image_type_id=event_image_type_id,
            image_license_type_id=event_image_license_type_id,
            image_source_name=file_metadata['source_name'],
            image_alt_text=event_image_alt,
            image_caption=event_image_caption,
            image_mime_type=file_metadata['mime_type'],
            image_width=file_metadata['width'],
            image_height=file_metadata['height']
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

    try:
        await db.commit()
        await db.refresh(new_event)
    except IntegrityError as e:
        await db.rollback()
        handle_integrity_error(e, ['organizer_id', 'venue_id'])

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


@router.get('/{event_date_id}/calendar', response_class=FileResponse)
async def get_event_calendar(
    event_date_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate and retrieve a calendar .ics file for the specified event date.
    """
    event = await get_event_detail_by_event_date_id(db, event_date_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No event date found for event_date_id: {event_date_id}'
        )

    # Validate that the required attributes are present
    required_attributes = ['event_title', 'event_description', 'event_date_start', 'event_venue_address']
    for attr in required_attributes:
        if not hasattr(event, attr):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Missing required attribute "{attr}" in event data.'
            )

    cal = Calendar()
    ical_event = ICalEvent()
    ical_event.add('summary', event.event_title)
    ical_event.add('description', event.event_description)
    ical_event.add('dtstart', event.event_date_start)

    if event.event_date_end:
        ical_event.add('dtend', event.event_date_end)

    ical_event.add('location', event.event_venue_address)
    cal.add_component(ical_event)

    ics_file_path = os.path.join(
        settings.TEMP_DIR, f'event_uranus_{event_date_id}.ics'
    )

    with open(ics_file_path, 'wb') as ics_file:
        ics_file.write(cal.to_ical())

    return FileResponse(
        ics_file_path,
        media_type='text/calendar',
        filename=f'event_uranus_{event_date_id}.ics'
    )

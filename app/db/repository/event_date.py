import re

from datetime import timezone

from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from app.schemas.event import EventCreate

from app.models.event_date import EventDate
from app.models.event import Event



async def create_event_date_entry(db: AsyncSession, event: EventCreate, new_event: Event):
    date_start = None
    date_end = None

    if event.event_date_start:
        date_start = event.event_date_start.replace(tzinfo=None)

    if event.event_date_end:
        date_end = event.event_date_end.replace(tzinfo=None)

    new_event_date = EventDate(
        date_start = date_start,
        date_end = date_end,
        event_id=new_event.id,
        venue_id=event.event_venue_id,
        space_id=event.event_space_id
    )   

    db.add(new_event_date)

    try:
        await db.commit()
        await db.refresh(new_event_date)

        return new_event_date
    except IntegrityError as e:
        await db.rollback()

        error_message = str(e.orig)
        match = re.search(r'\(([a-zA-Z\_]+)\)=\((-?\d+)\)', error_message)

        if match:
            column_name = match.group(1)
            column_value = match.group(2)

            if column_name in ['venue_id', 'space_id', 'organizer_id']:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'The {column_name} ({column_value}) provided is invalid.'
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Foreign key constraint violation.'
            )

from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.schemas.event_type_response import EventTypeResponse

from app.db.repository.event_type import get_all_event_types

from typing import List, Optional


router = APIRouter()


@router.get('/', response_model=List[EventTypeResponse])
async def fetch_all_event_types(
    lang: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    event_types = await get_all_event_types(db, lang)

    return event_types

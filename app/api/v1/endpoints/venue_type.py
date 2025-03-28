from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.schemas.venue_type_response import VenueTypeResponse

from app.db.repository.venue_type import get_all_venue_types


router = APIRouter()


@router.get('/', response_model=List[VenueTypeResponse])
async def fetch_all_venue_types(
    lang: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    venue_types = await get_all_venue_types(db, lang)

    return venue_types

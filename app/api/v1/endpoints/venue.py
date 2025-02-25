from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.venue import Venue
from app.db.repository.venue import get_all_venues
from typing import List



router = APIRouter()

@router.get('/', response_model=List[Venue])
async def fetch_all_venues(db: AsyncSession = Depends(get_db)):
    venues = await get_all_venues(db)

    return venues

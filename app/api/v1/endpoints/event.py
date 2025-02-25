from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.event import Event
from app.db.repository.event import get_all_events
from typing import List



router = APIRouter()

@router.get('/', response_model=List[Event])
async def fetch_all_events(db: AsyncSession = Depends(get_db)):
    events = await get_all_events(db)

    return events

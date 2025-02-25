from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.space import Space
from app.db.repository.space import get_all_spaces
from typing import List



router = APIRouter()

@router.get('/', response_model=List[Space])
async def fetch_all_spaces(db: AsyncSession = Depends(get_db)):
    spaces = await get_all_spaces(db)

    return spaces

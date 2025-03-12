from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.genre_type_response import GenreTypeResponse
from app.db.repository.genre_type import get_all_genre_types
from typing import List, Optional



router = APIRouter()

@router.get('/', response_model=List[GenreTypeResponse])
async def fetch_all_genre_types(
    lang: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    genre_types = await get_all_genre_types(db, lang)

    return genre_types

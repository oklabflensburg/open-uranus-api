from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.schemas.image_type_response import ImageTypeResponse

from app.db.repository.image_type import get_all_image_types

from typing import List, Optional



router = APIRouter()

@router.get('/', response_model=List[ImageTypeResponse])
async def fetch_all_image_types(
    lang: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    image_types = await get_all_image_types(db, lang)

    return image_types

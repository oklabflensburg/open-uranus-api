from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.schemas.license_type_response import LicenseTypeResponse

from app.db.repository.license_type import get_all_license_types

from typing import List, Optional



router = APIRouter()

@router.get('/', response_model=List[LicenseTypeResponse])
async def fetch_all_license_types(
    lang: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    licence_types = await get_all_license_types(db, lang)

    return licence_types

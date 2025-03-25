from app.schemas.country import CountryResponse
from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.db.repository.country import (
    get_all_countrys,
    get_country_by_name,
    get_country_by_code
)

from typing import List


router = APIRouter()


@router.get('/', response_model=List[CountryResponse])
async def fetch_all_countrys(
    lang: str,
    db: AsyncSession = Depends(get_db)
):
    countrys = await get_all_countrys(db, lang)

    return countrys


@router.get('/name', response_model=CountryResponse)
async def fetch_country_by_name(
    country_name: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    country = await get_country_by_name(db, country_name)

    return country


@router.get('/code', response_model=List[CountryResponse])
async def fetch_country_by_code(
    country_code: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    country = await get_country_by_code(db, country_code)

    return country

from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.schemas.i18n_locale import I18nLocaleResponse

from app.db.repository.i18n_locale import get_all_i18n_locales

from typing import List, Optional



router = APIRouter()

@router.get('/', response_model=List[I18nLocaleResponse])
async def fetch_all_i18n_locales(
    lang: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    i18n_locales = await get_all_i18n_locales(db, lang)

    return i18n_locales

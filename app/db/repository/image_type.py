from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.i18n_locale import I18nLocale
from app.models.image_type import ImageType



async def get_all_image_types(db: AsyncSession, lang: str):
    stmt = (
        select(
            ImageType.type_id.label('image_type_id'),
            ImageType.name.label('image_type_name'),
            ImageType.i18n_locale_id.label('image_locale_id')
        ).join(I18nLocale, I18nLocale.id == ImageType.i18n_locale_id)
    )

    if lang:
        stmt = stmt.where(I18nLocale.iso_639_1 == lang)

    result = await db.execute(stmt)
    images = result.mappings().all()

    return images

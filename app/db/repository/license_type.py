from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.i18n_locale import I18nLocale
from app.models.license_type import LicenseType



async def get_all_license_types(db: AsyncSession, lang: str):
    stmt = (
        select(
            LicenseType.id.label('license_type_id'),
            LicenseType.name.label('license_type_name'),
            LicenseType.i18n_locale_id.label('license_locale_id')
        ).join(I18nLocale, I18nLocale.id == LicenseType.i18n_locale_id)
    )

    if lang:
        stmt = stmt.where(I18nLocale.iso_639_1 == lang)

    stmt = stmt.order_by(LicenseType.name)

    result = await db.execute(stmt)
    licenses = result.mappings().all()

    return licenses

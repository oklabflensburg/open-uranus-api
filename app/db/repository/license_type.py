from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.license_type import LicenseType



async def get_all_license_types(db: AsyncSession, lang: str):
    stmt = (
        select(
            LicenseType.id.label('license_type_id'),
            LicenseType.name.label('license_type_name')
        )
    )

    result = await db.execute(stmt)
    licenses = result.mappings().all()

    return licenses

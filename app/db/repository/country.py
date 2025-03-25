from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.country import Country


async def get_all_countrys(db: AsyncSession):
    stmt = (
        select(
            Country.name.label('country_name'),
            Country.code.label('country_code'),
            Country.iso_639_1.label('country_iso_639_1'),
        ).order_by(Country.name)
    )

    countrys = await db.execute(stmt)
    result = countrys.mappings().all()

    return result


async def get_country_by_name(db: AsyncSession, country_name: str):
    stmt = (
        select(
            Country.name.label('country_name'),
            Country.code.label('country_code'),
            Country.iso_639_1.label('country_iso_639_1'),
        )
        .where(Country.name == country_name)
    )

    country = await db.execute(stmt)
    result = country.mappings().first()

    return result


async def get_country_by_code(db: AsyncSession, country_code: str):
    stmt = (
        select(
            Country.name.label('country_name'),
            Country.code.label('country_code'),
            Country.iso_639_1.label('country_iso_639_1'),
        )
        .where(Country.code == country_code)
    )

    country = await db.execute(stmt)
    result = country.mappings().all()

    return result

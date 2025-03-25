from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.state import State


async def get_all_states(db: AsyncSession):
    stmt = (
        select(
            State.name.label('state_name'),
            State.code.label('state_code'),
            State.country_code.label('state_country_code'),
        ).order_by(State.name)
    )

    states = await db.execute(stmt)
    result = states.mappings().all()

    return result


async def get_state_by_name(db: AsyncSession, state_name: str):
    stmt = (
        select(
            State.name.label('state_name'),
            State.code.label('state_code'),
            State.country_code.label('state_country_code'),
        )
        .where(State.name == state_name)
    )

    state = await db.execute(stmt)
    result = state.mappings().first()

    return result


async def get_state_by_code(db: AsyncSession, state_code: str):
    stmt = (
        select(
            State.name.label('state_name'),
            State.code.label('state_code'),
            State.country_code.label('state_country_code'),
        )
        .where(State.code == state_code)
    )

    state = await db.execute(stmt)
    result = state.mappings().first()

    return result

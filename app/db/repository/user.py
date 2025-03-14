from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User



async def get_user_by_id(db: AsyncSession, user_id: int):
    stmt = (
        select(User).where(User.id == user_id)
    )

    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    return user



async def get_user_by_username(db: AsyncSession, username: int):
    stmt = (
        select(User).where(User.username == username)
    )

    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    return user



async def get_user_by_email(db: AsyncSession, email_address: int):
    stmt = (
        select(User).where(User.email_address == email_address)
    )

    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    return user

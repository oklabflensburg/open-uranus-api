from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organizer import Organizer
from app.models.user import User
from app.models.user_role import UserRole
from app.models.user_organizer_links import UserOrganizerLinks


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


async def get_user_roles_by_current_user_id(db: AsyncSession, user_id: int):
    stmt = (
        select(
            Organizer.name.label('organizer_name'),
            UserRole.organization.label('role_organization'),
            UserRole.venue.label('role_venue'),
            UserRole.space.label('role_space'),
            UserRole.event.label('role_event')
        )
        .join(
            UserOrganizerLinks,
            UserOrganizerLinks.organizer_id == Organizer.id
        )
        .join(User, UserOrganizerLinks.user_id == User.id)
        .join(UserRole, UserRole.id == UserOrganizerLinks.user_role_id)
        .where(User.id == user_id)
    )

    result = await db.execute(stmt)
    rows = result.mappings().all()

    return rows

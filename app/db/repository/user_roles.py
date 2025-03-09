from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.user_role import UserRole
from app.models.user_venue_links import UserVenueLinks



async def get_roles_venue_by_user_id(db: AsyncSession, user_id: int):
    stmt = (
        select(
            User.id.label('user_id'),
            UserVenueLinks.venue_id,
            UserVenueLinks.user_role_id,
            UserRole.name.label('venue_name'),
            UserRole.organization.label('is_organization_editor'),
            UserRole.venue.label('is_venue_editor'),
            UserRole.space.label('is_space_editor'),
            UserRole.event.label('is_event_editor'),
            UserRole.venue_type.label('is_venue_type_editor'),
            UserRole.space_type.label('is_space_type_editor'),
            UserRole.event_type.label('is_event_type_editor'),
            UserRole.genre_type.label('is_genre_type_editor'),
            UserRole.image_type.label('is_image_type_editor'),
            UserRole.license_type.label('is_license_type_editor'),
        )
        .join(UserVenueLinks, UserVenueLinks.user_id == User.id)
        .join(UserRole, UserRole.id == UserVenueLinks.user_role_id)
        .where(User.id == user_id, UserRole.venue.is_(True))
    )

    result = await db.execute(stmt)
    user_venues = result.mappings().all()
    return user_venues

import re

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user_roles_venue_response import UserRolesVenueResponse

from app.db.repository.user_roles import get_roles_venue_by_user_id

from app.models.user_venue_links import UserVenueLinks
from app.models.user import User

from app.services.auth import get_current_user

from app.db.session import get_db



router = APIRouter()


@router.post('/venue', response_model=UserVenueLinks)
async def create_user_venue_link(
    venue_id: int,
    user_role_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_user_venue_link = UserVenueLinks(
        user_id=current_user.id,
        venue_id=venue_id,
        user_role_id=user_role_id
    )
    
    try:
        db.add(new_user_venue_link)

        await db.commit()
        await db.refresh(new_user_venue_link)

        return new_user_venue_link
    except IntegrityError as e:
        await db.rollback()

        error_message = str(e.orig)
        match = re.search(r'\(([a-zA-Z\_]+)\)=\((-?\d+)\)', error_message)

        if match:
            column_name = match.group(1)
            column_value = match.group(2)

            if column_name == 'venue_id':
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'The venue_id ({column_value}) provided does not exist.'
                )
            elif column_name == 'user_role_id':
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'The user_role_id ({column_value}) provided is invalid.'
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'Foreign key constraint failed on column {column_name} with value {column_value}.'
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Foreign key constraint violation.'
            )



@router.get('/venue', response_model=List[UserRolesVenueResponse])
async def fetch_roles_venue_by_user_id(
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
    user_roles = await get_roles_venue_by_user_id(db, current_user.id)

    return user_roles

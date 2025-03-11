from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from app.db.session import get_db

from app.services.auth import get_current_user

from app.db.repository.organizer import get_organizer_by_user_id, create_organizer_entry

from app.schemas.organizer import OrganizerRead, OrganizerCreate

from app.models.organizer import Organizer

from app.models.user import User



router = APIRouter()


@router.post('/', response_model=Organizer, status_code=status.HTTP_201_CREATED)
async def create_organizer(
    organizer: OrganizerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_organizer = await create_organizer_entry(db, organizer)

    return new_organizer



@router.get('/', response_model=List[OrganizerRead])
async def fetch_organizer_by_user_id(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    organizer = await get_organizer_by_user_id(db, current_user.id)

    return organizer

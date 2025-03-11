from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from app.db.session import get_db

from app.services.auth import get_current_user

from app.schemas.organizer import OrganizerRead

from app.db.repository.organizer import get_organizer_by_user_id

from app.models.organizer import Organizer, OrganizerCreate

from app.models.user import User



router = APIRouter()


@router.post('/', response_model=OrganizerRead, status_code=status.HTTP_201_CREATED)
async def create_organizer(
    organizer: OrganizerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_organizer = Organizer(**organizer.dict())
    db.add(db_organizer)

    await db.commit()
    await db.refresh(db_organizer)

    return db_organizer



@router.get('/', response_model=List[OrganizerRead])
async def fetch_organizer_by_user_id(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    organizer = await get_organizer_by_user_id(db, current_user.id)

    return organizer

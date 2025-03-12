from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from app.db.session import get_db

from app.services.auth import get_current_user

from app.db.repository.organizer import add_user_organizer, add_organizer

from app.schemas.organizer import OrganizerRead, OrganizerCreate, OrganizerCreateResponse

from app.models.organizer import Organizer

from app.models.user import User



router = APIRouter()


@router.post('/', response_model=OrganizerCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_organizer(
    organizer: OrganizerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    current_user_email = current_user.email_address

    new_organizer = await add_organizer(db, organizer, current_user_email)
    new_user_organizer = await add_user_organizer(
        db, current_user.id, new_organizer.id, 1
    )

    return OrganizerCreateResponse(
        organizer_id=new_organizer.id,
        organizer_name=new_organizer.name,
        organizer_description=new_organizer.description,
        organizer_contact_email=new_organizer.contact_email,
        organizer_contact_phone=new_organizer.contact_phone,
        organizer_website_url=new_organizer.website_url,
        organizer_street=new_organizer.street,
        organizer_house_number=new_organizer.house_number,
        organizer_postal_code=new_organizer.postal_code,
        organizer_city=new_organizer.city
    )

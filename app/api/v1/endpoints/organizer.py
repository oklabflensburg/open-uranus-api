from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.services.auth import get_current_user

from app.db.repository.organizer import get_organizer_stats, add_user_organizer, add_organizer

from app.schemas.organizer import OrganizerCreate, OrganizerCreateResponse

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



@router.get('/stats', response_model=dict)
async def fetch_organizer_stats(
    organizer_id: int,
    db: AsyncSession = Depends(get_db)
):
    stats = await get_organizer_stats(db, organizer_id)

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No stats found for organizer_id: {organizer_id}'
        )

    return stats
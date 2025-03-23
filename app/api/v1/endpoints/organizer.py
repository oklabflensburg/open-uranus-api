from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.models.organizer import Organizer
from app.services.auth import get_current_user

from app.db.repository.organizer import (
    get_organizer_stats,
    get_organizer_by_id,
    add_user_organizer,
    add_organizer
)

from app.schemas.organizer import OrganizerCreate, OrganizerSchema

from app.models.user import User


router = APIRouter()


@router.post('/', response_model=OrganizerSchema, status_code=status.HTTP_201_CREATED)
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

    return OrganizerSchema(
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


@router.get(
    '/{organizer_id}', 
    response_model=OrganizerSchema,
)
async def fetch_organizer_by_id(
    organizer_id: int,
    db: AsyncSession = Depends(get_db)
):
    organizer = await get_organizer_by_id(db, organizer_id)
    print(organizer)
    if not organizer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Organizer with id {organizer_id} not found'
        )

    return OrganizerSchema(
        organizer_id=organizer.id,
        organizer_name=organizer.name,
        organizer_description=organizer.description,
        organizer_contact_email=organizer.contact_email,
        organizer_contact_phone=organizer.contact_phone,
        organizer_website_url=organizer.website_url,
        organizer_street=organizer.street,
        organizer_house_number=organizer.house_number,
        organizer_postal_code=organizer.postal_code,
        organizer_city=organizer.city
    )


@router.put('/{organizer_id}', response_model=OrganizerSchema)
async def update_organizer_by_id(
    organizer_id: int,
    organizer_schema: OrganizerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    organizer = await get_organizer_by_id(db, organizer_id)
    
    if not organizer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Organizer with id {organizer_id} not found'
        )
    
    organizer.name = organizer_schema.organizer_name
    organizer.description = organizer_schema.organizer_description
    organizer.contact_email = organizer_schema.organizer_contact_email
    organizer.contact_phone = organizer_schema.organizer_contact_phone
    organizer.website_url = organizer_schema.organizer_website_url
    organizer.street = organizer_schema.organizer_street
    organizer.house_number = organizer_schema.organizer_house_number
    organizer.postal_code = organizer_schema.organizer_postal_code
    organizer.city = organizer_schema.organizer_city
    
    try:
        await db.commit()
        await db.refresh(organizer)
    except Exception as e:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to update organizer: {str(e)}'
        )
    
    return OrganizerSchema(
        organizer_id=organizer.id,
        organizer_name=organizer.name,
        organizer_description=organizer.description,
        organizer_contact_email=organizer.contact_email,
        organizer_contact_phone=organizer.contact_phone,
        organizer_website_url=organizer.website_url,
        organizer_street=organizer.street,
        organizer_house_number=organizer.house_number,
        organizer_postal_code=organizer.postal_code,
        organizer_city=organizer.city
    )
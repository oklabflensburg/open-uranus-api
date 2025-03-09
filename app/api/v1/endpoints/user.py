from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError

from sqlmodel import select
from pydantic import EmailStr

from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.services.auth import verify_password, create_access_token, get_current_user

from app.schemas.user_roles_venue_response import UserRolesVenueResponse
from app.schemas.user import UserRead, UserCreate, UserUpdate, UserSignin, Token

from app.models.user import User
from app.db.repository.user_roles import get_roles_venue_by_user_id

from app.db.session import get_db



router = APIRouter()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.post('/signup', response_model=UserRead)
async def signup_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    hashed_password = pwd_context.hash(user.password)
    print(hashed_password)
    new_user = User(**user.dict(exclude={'password'}), password_hash=hashed_password)

    try:
        db.add(new_user)
        await db.flush()
        await db.commit()
        await db.refresh(new_user)

        return new_user
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User with email address or username already exists'
        )



@router.post('/signin', response_model=Token)
async def signin_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.username == form_data.username))
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    access_token = create_access_token(data={'sub': db_user.username})

    return {'access_token': access_token, 'token_type': 'bearer'}



@router.put('/update-user', response_model=UserRead)
async def update_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Fetch the user from the database
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    # Prevent updating username and email
    update_data = user_update.dict(exclude_unset=True)

    if 'username' in update_data or 'email_address' in update_data:
        raise HTTPException(
            status_code=400, detail='Username and email cannot be changed'
        )

    # Hash password if being updated
    if 'password' in update_data:
        update_data['password_hash'] = pwd_context.hash(update_data.pop('password'))

    for key, value in update_data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    return user



@router.post('/change-email')
async def user_change_email(
    new_email: EmailStr,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check if new email already exists
    result = await db.execute(select(User).where(User.email_address == new_email))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail='Email already in use')

    # Send a verification email before updating (Example)
    send_verification_email(current_user, new_email)

    return {'message': 'Verification email sent. Please confirm to update email.'}



@router.get('/profile', response_model=UserRead)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user



@router.get('/roles/venue', response_model=List[UserRolesVenueResponse])
async def fetch_roles_venue_by_user_id(
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
    user_roles = await get_roles_venue_by_user_id(db, current_user.id)
    return user_roles

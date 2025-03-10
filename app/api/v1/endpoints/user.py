from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError

from sqlmodel import select
from pydantic import EmailStr

from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.services.auth import verify_password, create_access_token, get_current_user

from app.schemas.user import UserRead, UserCreate, UserUpdate, UserSignin, Token

from app.models.user import User

from app.db.repository.user import get_user_by_id, get_user_by_username, get_user_by_email
from app.db.session import get_db



router = APIRouter()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.post('/signup', response_model=UserRead)
async def signup_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    hashed_password = pwd_context.hash(user.password)
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
    db_user = await get_user_by_username(db, form_data.username)

    if not db_user or not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    access_token = create_access_token(data={'sub': db_user.username})

    return {'access_token': access_token, 'token_type': 'bearer'}



@router.put('/update', response_model=UserRead)
async def update_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = await get_user_by_id(db, current_user.id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User not found by user id {current_user.id}'
        )

    # Prevent updating username and email
    update_data = user_update.dict(exclude_unset=True)

    if 'username' in update_data or 'email_address' in update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username and email address cannot be changed here'
        )

    # Hash password if being updated
    if 'password' in update_data:
        update_data['password_hash'] = pwd_context.hash(update_data.pop('password'))

    for key, value in update_data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    return user



@router.post('/update/email')
async def user_change_email(
    new_email: EmailStr,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = await get_user_by_email(db, new_email)

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email address already in use'
        )

    # Send a verification email before updating (Example)
    # send_verification_email(current_user, new_email)

    return {'message': 'Verification email sent. Please confirm to update email.'}



@router.get('/profile', response_model=UserRead)
async def fetch_user_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user

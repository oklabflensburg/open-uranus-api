from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlmodel import select

from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.services.auth import verify_password, create_access_token, get_current_user

from app.schemas.user import UserRead, UserCreate
from app.schemas.user import UserLogin, Token

from app.models.user import User

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

    db.add(new_user)

    await db.flush()
    await db.commit()
    await db.refresh(new_user)

    return new_user



@router.post('/login', response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.username == form_data.username))
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token = create_access_token(data={'sub': db_user.username})

    return {'access_token': access_token, 'token_type': 'bearer'}



@router.get('/profile', response_model=UserRead)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

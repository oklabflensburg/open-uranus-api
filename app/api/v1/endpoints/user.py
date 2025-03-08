from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserRead, UserCreate
from passlib.context import CryptContext

from app.db.session import get_db
from app.models.user import User



router = APIRouter()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.post('/signup', response_model=UserRead)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    hashed_password = pwd_context.hash(user.password_hash)
    new_user = User(**user.dict(exclude={'password_hash'}), password_hash=hashed_password)

    db.add(new_user)

    await db.flush()
    await db.commit()
    await db.refresh(new_user)

    return new_user



@router.post('/signin')
def login():
    # Implement token-based authentication (JWT)
    pass

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import User
from app.schemas.user import UserRead, UserCreate
from app.db.repository.event_type import get_all_event_types

from typing import List, Optional



router = APIRouter()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.post('/register', response_model=UserRead)
def register_user(user: UserCreate, session: Session = Depends(get_session)):
    hashed_password = pwd_context.hash(user.password_hash)
    new_user = User(**user.dict(), password_hash=hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user



@router.get('/', response_model=List[EventTypeResponse])
async def fetch_all_event_types(
    db: AsyncSession = Depends(get_db)
):
    event_types = await get_all_event_types(db)

    return event_types

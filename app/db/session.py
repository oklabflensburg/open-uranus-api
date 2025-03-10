from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.core.config import settings



# Create the async engine
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)


# Create a session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# Initialize database tables
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# Dependency to get the db session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings



engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Create a session factory
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency to get the db session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

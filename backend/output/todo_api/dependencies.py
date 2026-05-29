from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from fastapi import Depends

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create an asynchronous engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create a configured "Session" class
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for our models
Base = declarative_base()

# Dependency for getting a database session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
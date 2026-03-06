"""
Database Dependencies for FastAPI
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get async database session

    Usage in endpoints:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...

    Yields:
        Async database session
    """
    async with AsyncSessionLocal() as session:
        yield session

"""
Database Dependencies for FastAPI
"""
from typing import Generator
from sqlalchemy.orm import Session

from app.common.database.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session

    Usage in endpoints:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
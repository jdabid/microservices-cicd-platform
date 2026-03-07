"""
Integration test fixtures
Shared conftest for TestClient-based integration tests.
"""
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.common.database.base import Base
from app.features.appointments.models.appointment import Appointment  # noqa: F401
from app.features.patients.models.patient import Patient  # noqa: F401
from app.features.auth.models.user import User
from app.common.dependencies.database import get_db
from app.core.security import hash_password, create_access_token
from app.main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db():
    """Create an in-memory SQLite database and override get_db."""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = TestingSessionLocal()

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_db):
    """TestClient with overridden database dependency."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(test_db, client):
    """Create a user directly in DB and return Authorization headers with a valid JWT."""
    user = User(
        email="auth@example.com",
        hashed_password=hash_password("TestPass123"),
        full_name="Auth User",
    )
    test_db.add(user)
    test_db.commit()

    token = create_access_token(data={"sub": user.email})
    return {"Authorization": f"Bearer {token}"}

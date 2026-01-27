"""
Pytest configuration and shared fixtures
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from app.common.database.base import Base
from app.features.appointments.models.appointment import Appointment, AppointmentStatus

# Test database URL (usar SQLite en memoria para tests)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine"""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create a test database session"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )

    session = TestingSessionLocal()

    yield session

    session.close()


@pytest.fixture
def sample_appointment_data():
    """Sample appointment data for testing"""
    return {
        "patient_name": "Test Patient",
        "patient_email": "test@example.com",
        "patient_phone": "+57 300 123 4567",
        "doctor_name": "Dr. Test",
        "specialty": "General",
        "appointment_date": datetime.now() + timedelta(days=7),
        "duration_minutes": 30,
        "reason": "Test appointment",
        "notes": "Test notes"
    }


@pytest.fixture
def create_test_appointment(db_session):
    """Factory fixture to create test appointments"""

    def _create_appointment(**kwargs):
        default_data = {
            "patient_name": "Test Patient",
            "patient_email": "test@example.com",
            "doctor_name": "Dr. Test",
            "specialty": "General",
            "appointment_date": datetime.now() + timedelta(days=7),
            "duration_minutes": 30,
            "status": AppointmentStatus.SCHEDULED
        }
        default_data.update(kwargs)

        appointment = Appointment(**default_data)
        db_session.add(appointment)
        db_session.commit()
        db_session.refresh(appointment)

        return appointment

    return _create_appointment
"""
Unit tests for Appointment Queries (CQRS Read Operations)
"""
import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.features.appointments.queries.get_appointment import GetAppointmentQuery
from app.features.appointments.queries.list_appointments import (
    ListAppointmentsQuery,
    GetUpcomingAppointmentsQuery
)
from app.features.appointments.models.appointment import AppointmentStatus


class TestGetAppointmentQuery:
    """Tests for GetAppointmentQuery"""

    @pytest.mark.asyncio
    async def test_get_appointment_success(self, db_session, create_test_appointment):
        """Test successful appointment retrieval"""
        # Arrange
        appointment = create_test_appointment()
        query = GetAppointmentQuery(db_session)

        # Act
        result = await query.execute(appointment.id)

        # Assert
        assert result.id == appointment.id
        assert result.patient_name == appointment.patient_name
        assert result.patient_email == appointment.patient_email

    @pytest.mark.asyncio
    async def test_get_nonexistent_appointment_fails(self, db_session):
        """Test getting non-existent appointment fails"""
        # Arrange
        query = GetAppointmentQuery(db_session)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await query.execute(999)

        assert exc_info.value.status_code == 404


class TestListAppointmentsQuery:
    """Tests for ListAppointmentsQuery"""

    @pytest.mark.asyncio
    async def test_list_appointments_empty(self, db_session):
        """Test listing appointments when none exist"""
        # Arrange
        query = ListAppointmentsQuery(db_session)

        # Act
        result = await query.execute(page=1, page_size=10)

        # Assert
        assert result["total"] == 0
        assert len(result["items"]) == 0
        assert result["page"] == 1
        assert result["total_pages"] == 0

    @pytest.mark.asyncio
    async def test_list_appointments_with_data(self, db_session, create_test_appointment):
        """Test listing appointments with data"""
        # Arrange
        create_test_appointment(patient_name="Patient 1")
        create_test_appointment(patient_name="Patient 2")
        create_test_appointment(patient_name="Patient 3")
        query = ListAppointmentsQuery(db_session)

        # Act
        result = await query.execute(page=1, page_size=10)

        # Assert
        assert result["total"] == 3
        assert len(result["items"]) == 3
        assert result["page"] == 1

    @pytest.mark.asyncio
    async def test_list_appointments_pagination(self, db_session, create_test_appointment):
        """Test appointment pagination"""
        # Arrange
        for i in range(5):
            create_test_appointment(patient_name=f"Patient {i + 1}")
        query = ListAppointmentsQuery(db_session)

        # Act - Page 1
        result_page1 = await query.execute(page=1, page_size=2)

        # Assert - Page 1
        assert result_page1["total"] == 5
        assert len(result_page1["items"]) == 2
        assert result_page1["page"] == 1
        assert result_page1["total_pages"] == 3

        # Act - Page 2
        result_page2 = await query.execute(page=2, page_size=2)

        # Assert - Page 2
        assert len(result_page2["items"]) == 2
        assert result_page2["page"] == 2

    @pytest.mark.asyncio
    async def test_list_appointments_filter_by_status(self, db_session, create_test_appointment):
        """Test filtering appointments by status"""
        # Arrange
        create_test_appointment(status=AppointmentStatus.SCHEDULED)
        create_test_appointment(status=AppointmentStatus.SCHEDULED)
        create_test_appointment(status=AppointmentStatus.COMPLETED)
        query = ListAppointmentsQuery(db_session)

        # Act
        result = await query.execute(
            page=1,
            page_size=10,
            status=AppointmentStatus.SCHEDULED
        )

        # Assert
        assert result["total"] == 2
        assert all(apt.status == AppointmentStatus.SCHEDULED for apt in result["items"])

    @pytest.mark.asyncio
    async def test_list_appointments_filter_by_patient_name(self, db_session, create_test_appointment):
        """Test filtering appointments by patient name"""
        # Arrange
        create_test_appointment(patient_name="John Doe")
        create_test_appointment(patient_name="Jane Doe")
        create_test_appointment(patient_name="Bob Smith")
        query = ListAppointmentsQuery(db_session)

        # Act
        result = await query.execute(
            page=1,
            page_size=10,
            patient_name="Doe"
        )

        # Assert
        assert result["total"] == 2


class TestGetUpcomingAppointmentsQuery:
    """Tests for GetUpcomingAppointmentsQuery"""

    @pytest.mark.asyncio
    async def test_get_upcoming_appointments(self, db_session, create_test_appointment):
        """Test getting upcoming appointments"""
        # Arrange
        now = datetime.now()
        create_test_appointment(
            appointment_date=now + timedelta(days=2),
            status=AppointmentStatus.SCHEDULED
        )
        create_test_appointment(
            appointment_date=now + timedelta(days=5),
            status=AppointmentStatus.CONFIRMED
        )
        create_test_appointment(
            appointment_date=now + timedelta(days=10),  # Outside 7 days
            status=AppointmentStatus.SCHEDULED
        )
        create_test_appointment(
            appointment_date=now - timedelta(days=1),  # Past
            status=AppointmentStatus.SCHEDULED
        )
        query = GetUpcomingAppointmentsQuery(db_session)

        # Act
        result = await query.execute(days_ahead=7)

        # Assert
        assert len(result) == 2  # Only 2 within next 7 days
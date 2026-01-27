"""
Unit tests for Appointment Commands (CQRS Write Operations)
"""
import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException

from app.features.appointments.commands.create_appointment import CreateAppointmentCommand
from app.features.appointments.commands.update_appointment import UpdateAppointmentCommand
from app.features.appointments.commands.cancel_appointment import CancelAppointmentCommand
from app.features.appointments.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.features.appointments.models.appointment import AppointmentStatus


class TestCreateAppointmentCommand:
    """Tests for CreateAppointmentCommand"""

    @pytest.mark.asyncio
    async def test_create_appointment_success(self, db_session, sample_appointment_data):
        """Test successful appointment creation"""
        # Arrange
        command = CreateAppointmentCommand(db_session)
        appointment_data = AppointmentCreate(**sample_appointment_data)

        # Act
        result = await command.execute(appointment_data)

        # Assert
        assert result.id is not None
        assert result.patient_name == sample_appointment_data["patient_name"]
        assert result.patient_email == sample_appointment_data["patient_email"]
        assert result.doctor_name == sample_appointment_data["doctor_name"]
        assert result.status == AppointmentStatus.SCHEDULED
        assert result.created_at is not None

    @pytest.mark.asyncio
    async def test_create_appointment_past_date_fails(self, db_session, sample_appointment_data):
        """Test appointment creation fails with past date"""
        # Arrange
        command = CreateAppointmentCommand(db_session)
        sample_appointment_data["appointment_date"] = datetime.now() - timedelta(days=1)

        # Act & Assert
        with pytest.raises(ValueError, match="future"):
            appointment_data = AppointmentCreate(**sample_appointment_data)

    @pytest.mark.asyncio
    async def test_create_appointment_too_far_future_fails(self, db_session, sample_appointment_data):
        """Test appointment creation fails when too far in future"""
        # Arrange
        command = CreateAppointmentCommand(db_session)
        sample_appointment_data["appointment_date"] = datetime.now() + timedelta(days=100)
        appointment_data = AppointmentCreate(**sample_appointment_data)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await command.execute(appointment_data)

        assert exc_info.value.status_code == 400
        assert "90 days" in str(exc_info.value.detail)


class TestUpdateAppointmentCommand:
    """Tests for UpdateAppointmentCommand"""

    @pytest.mark.asyncio
    async def test_update_appointment_success(self, db_session, create_test_appointment):
        """Test successful appointment update"""
        # Arrange
        appointment = create_test_appointment()
        command = UpdateAppointmentCommand(db_session)
        update_data = AppointmentUpdate(
            patient_name="Updated Name",
            reason="Updated reason"
        )

        # Act
        result = await command.execute(appointment.id, update_data)

        # Assert
        assert result.id == appointment.id
        assert result.patient_name == "Updated Name"
        assert result.reason == "Updated reason"
        assert result.patient_email == appointment.patient_email  # Unchanged

    @pytest.mark.asyncio
    async def test_update_nonexistent_appointment_fails(self, db_session):
        """Test updating non-existent appointment fails"""
        # Arrange
        command = UpdateAppointmentCommand(db_session)
        update_data = AppointmentUpdate(patient_name="Test")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await command.execute(999, update_data)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_cancelled_appointment_fails(self, db_session, create_test_appointment):
        """Test updating cancelled appointment fails"""
        # Arrange
        appointment = create_test_appointment(status=AppointmentStatus.CANCELLED)
        command = UpdateAppointmentCommand(db_session)
        update_data = AppointmentUpdate(patient_name="New Name")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await command.execute(appointment.id, update_data)

        assert exc_info.value.status_code == 400
        assert "cancelled" in str(exc_info.value.detail).lower()


class TestCancelAppointmentCommand:
    """Tests for CancelAppointmentCommand"""

    @pytest.mark.asyncio
    async def test_cancel_appointment_success(self, db_session, create_test_appointment):
        """Test successful appointment cancellation"""
        # Arrange
        appointment = create_test_appointment()
        command = CancelAppointmentCommand(db_session)

        # Act
        result = await command.execute(appointment.id)

        # Assert
        assert result.id == appointment.id
        assert result.status == AppointmentStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_appointment_fails(self, db_session):
        """Test cancelling non-existent appointment fails"""
        # Arrange
        command = CancelAppointmentCommand(db_session)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await command.execute(999)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_cancel_already_cancelled_fails(self, db_session, create_test_appointment):
        """Test cancelling already cancelled appointment fails"""
        # Arrange
        appointment = create_test_appointment(status=AppointmentStatus.CANCELLED)
        command = CancelAppointmentCommand(db_session)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await command.execute(appointment.id)

        assert exc_info.value.status_code == 400
        assert "already cancelled" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_cancel_completed_appointment_fails(self, db_session, create_test_appointment):
        """Test cancelling completed appointment fails"""
        # Arrange
        appointment = create_test_appointment(status=AppointmentStatus.COMPLETED)
        command = CancelAppointmentCommand(db_session)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await command.execute(appointment.id)

        assert exc_info.value.status_code == 400
        assert "completed" in str(exc_info.value.detail).lower()
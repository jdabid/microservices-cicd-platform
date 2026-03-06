"""
Unit tests for patient commands (create, update, delete)
"""
import pytest

from app.common.exceptions import BadRequestException, ConflictException, NotFoundException
from app.features.patients.commands.create_patient import CreatePatientCommand
from app.features.patients.commands.delete_patient import DeletePatientCommand
from app.features.patients.commands.update_patient import UpdatePatientCommand
from app.features.patients.models.patient import Patient
from app.features.patients.schemas.patient import PatientCreate, PatientUpdate


class TestCreatePatientCommand:
    """Tests for CreatePatientCommand."""

    @pytest.mark.asyncio
    async def test_create_success(self, db_session) -> None:
        command = CreatePatientCommand(db_session)
        data = PatientCreate(
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            phone="+57 300 111 2222",
        )

        patient = await command.execute(data)

        assert patient.id is not None
        assert patient.first_name == "Jane"
        assert patient.last_name == "Doe"
        assert patient.email == "jane@example.com"
        assert patient.is_active is True

    @pytest.mark.asyncio
    async def test_create_duplicate_email_raises(self, db_session) -> None:
        existing = Patient(
            first_name="Existing",
            last_name="User",
            email="dup@example.com",
        )
        db_session.add(existing)
        db_session.commit()

        command = CreatePatientCommand(db_session)
        data = PatientCreate(
            first_name="Another",
            last_name="User",
            email="dup@example.com",
        )

        with pytest.raises(ConflictException):
            await command.execute(data)


class TestUpdatePatientCommand:
    """Tests for UpdatePatientCommand."""

    @pytest.mark.asyncio
    async def test_update_success(self, db_session) -> None:
        patient = Patient(
            first_name="Old", last_name="Name", email="update@example.com"
        )
        db_session.add(patient)
        db_session.commit()

        command = UpdatePatientCommand(db_session)
        data = PatientUpdate(first_name="New")

        updated = await command.execute(patient.id, data)

        assert updated.first_name == "New"
        assert updated.last_name == "Name"

    @pytest.mark.asyncio
    async def test_update_not_found_raises(self, db_session) -> None:
        command = UpdatePatientCommand(db_session)
        data = PatientUpdate(first_name="Ghost")

        with pytest.raises(NotFoundException):
            await command.execute(9999, data)

    @pytest.mark.asyncio
    async def test_update_duplicate_email_raises(self, db_session) -> None:
        p1 = Patient(first_name="A", last_name="A", email="a@example.com")
        p2 = Patient(first_name="B", last_name="B", email="b@example.com")
        db_session.add_all([p1, p2])
        db_session.commit()

        command = UpdatePatientCommand(db_session)
        data = PatientUpdate(email="a@example.com")

        with pytest.raises(ConflictException):
            await command.execute(p2.id, data)


class TestDeletePatientCommand:
    """Tests for DeletePatientCommand."""

    @pytest.mark.asyncio
    async def test_delete_success(self, db_session) -> None:
        patient = Patient(
            first_name="Delete", last_name="Me", email="delete@example.com"
        )
        db_session.add(patient)
        db_session.commit()

        command = DeletePatientCommand(db_session)
        deleted = await command.execute(patient.id)

        assert deleted.is_active is False

    @pytest.mark.asyncio
    async def test_delete_not_found_raises(self, db_session) -> None:
        command = DeletePatientCommand(db_session)

        with pytest.raises(NotFoundException):
            await command.execute(9999)

    @pytest.mark.asyncio
    async def test_delete_already_inactive_raises(self, db_session) -> None:
        patient = Patient(
            first_name="Inactive",
            last_name="Patient",
            email="inactive@example.com",
            is_active=False,
        )
        db_session.add(patient)
        db_session.commit()

        command = DeletePatientCommand(db_session)

        with pytest.raises(BadRequestException):
            await command.execute(patient.id)

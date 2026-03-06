"""
Unit tests for patient queries (get, list)
"""
import pytest

from app.common.exceptions import NotFoundException
from app.features.patients.models.patient import Patient
from app.features.patients.queries.get_patient import GetPatientQuery
from app.features.patients.queries.list_patients import ListPatientsQuery


class TestGetPatientQuery:
    """Tests for GetPatientQuery."""

    @pytest.mark.asyncio
    async def test_get_success(self, db_session) -> None:
        patient = Patient(
            first_name="Found", last_name="Patient", email="found@example.com"
        )
        db_session.add(patient)
        db_session.commit()

        query = GetPatientQuery(db_session)
        result = await query.execute(patient.id)

        assert result.id == patient.id
        assert result.email == "found@example.com"

    @pytest.mark.asyncio
    async def test_get_not_found_raises(self, db_session) -> None:
        query = GetPatientQuery(db_session)

        with pytest.raises(NotFoundException):
            await query.execute(9999)


class TestListPatientsQuery:
    """Tests for ListPatientsQuery."""

    @pytest.mark.asyncio
    async def test_list_empty(self, db_session) -> None:
        query = ListPatientsQuery(db_session)
        result = await query.execute()

        assert result["total"] == 0
        assert result["items"] == []

    @pytest.mark.asyncio
    async def test_list_with_patients(self, db_session) -> None:
        for i in range(3):
            db_session.add(
                Patient(
                    first_name=f"Patient{i}",
                    last_name=f"Last{i}",
                    email=f"p{i}@example.com",
                )
            )
        db_session.commit()

        query = ListPatientsQuery(db_session)
        result = await query.execute()

        assert result["total"] == 3
        assert len(result["items"]) == 3

    @pytest.mark.asyncio
    async def test_list_search_filter(self, db_session) -> None:
        db_session.add(
            Patient(first_name="Alice", last_name="Smith", email="alice@example.com")
        )
        db_session.add(
            Patient(first_name="Bob", last_name="Jones", email="bob@example.com")
        )
        db_session.commit()

        query = ListPatientsQuery(db_session)
        result = await query.execute(search="Alice")

        assert result["total"] == 1
        assert result["items"][0].first_name == "Alice"

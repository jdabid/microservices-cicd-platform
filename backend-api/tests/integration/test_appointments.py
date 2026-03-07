"""
Integration tests for appointments feature (US-14)
Tests the full HTTP request/response cycle via TestClient.
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def mock_celery(monkeypatch):
    """Prevent Celery tasks from being dispatched during tests."""
    mock_task = MagicMock()
    monkeypatch.setattr(
        "app.features.appointments.commands.create_appointment.send_appointment_confirmation_email",
        mock_task,
    )


def _future_date() -> str:
    return (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()


def _appointment_payload(**overrides) -> dict:
    data = {
        "patient_name": "Test Patient",
        "patient_email": "patient@example.com",
        "patient_phone": "+57 300 123 4567",
        "doctor_name": "Dr. Test",
        "specialty": "General",
        "appointment_date": _future_date(),
        "duration_minutes": 30,
        "reason": "Checkup",
        "notes": "Integration test",
    }
    data.update(overrides)
    return data


class TestCreateAppointment:
    def test_create_appointment_success(self, client):
        response = client.post("/api/v1/appointments/", json=_appointment_payload())

        assert response.status_code == 201
        body = response.json()
        assert body["patient_name"] == "Test Patient"
        assert body["status"] == "scheduled"
        assert "id" in body

    def test_create_appointment_invalid_date(self, client):
        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        response = client.post(
            "/api/v1/appointments/", json=_appointment_payload(appointment_date=past)
        )

        assert response.status_code == 422


class TestGetAppointment:
    def test_get_appointment_success(self, client):
        create = client.post("/api/v1/appointments/", json=_appointment_payload())
        appt_id = create.json()["id"]

        response = client.get(f"/api/v1/appointments/{appt_id}")

        assert response.status_code == 200
        assert response.json()["id"] == appt_id

    def test_get_appointment_not_found(self, client):
        response = client.get("/api/v1/appointments/9999")

        assert response.status_code == 404


class TestListAppointments:
    def test_list_appointments_empty(self, client):
        response = client.get("/api/v1/appointments/")

        assert response.status_code == 200
        body = response.json()
        assert body["items"] == []
        assert body["total"] == 0

    def test_list_appointments_with_data(self, client):
        client.post("/api/v1/appointments/", json=_appointment_payload())
        client.post(
            "/api/v1/appointments/",
            json=_appointment_payload(patient_name="Second Patient"),
        )

        response = client.get("/api/v1/appointments/")

        assert response.status_code == 200
        assert response.json()["total"] == 2


class TestCancelAppointment:
    def test_cancel_appointment_success(self, client):
        create = client.post("/api/v1/appointments/", json=_appointment_payload())
        appt_id = create.json()["id"]

        response = client.delete(f"/api/v1/appointments/{appt_id}")

        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"


class TestUpdateAppointment:
    def test_update_appointment_success(self, client):
        create = client.post("/api/v1/appointments/", json=_appointment_payload())
        appt_id = create.json()["id"]

        response = client.put(
            f"/api/v1/appointments/{appt_id}",
            json={"doctor_name": "Dr. Updated"},
        )

        assert response.status_code == 200
        assert response.json()["doctor_name"] == "Dr. Updated"

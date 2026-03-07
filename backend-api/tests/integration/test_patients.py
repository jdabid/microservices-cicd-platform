"""
Integration tests for patients feature (US-15)
Tests the full HTTP request/response cycle via TestClient.
"""


def _patient_payload(**overrides) -> dict:
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+57 300 111 2222",
        "date_of_birth": "1990-01-15",
        "gender": "male",
        "address": "123 Test St",
    }
    data.update(overrides)
    return data


class TestCreatePatient:
    def test_create_patient_success(self, client):
        response = client.post("/api/v1/patients/", json=_patient_payload())

        assert response.status_code == 201
        body = response.json()
        assert body["first_name"] == "John"
        assert body["last_name"] == "Doe"
        assert body["is_active"] is True
        assert "id" in body

    def test_create_duplicate_patient(self, client):
        client.post("/api/v1/patients/", json=_patient_payload())
        response = client.post("/api/v1/patients/", json=_patient_payload())

        assert response.status_code == 409


class TestGetPatient:
    def test_get_patient_success(self, client):
        create = client.post("/api/v1/patients/", json=_patient_payload())
        patient_id = create.json()["id"]

        response = client.get(f"/api/v1/patients/{patient_id}")

        assert response.status_code == 200
        assert response.json()["email"] == "john.doe@example.com"

    def test_get_patient_not_found(self, client):
        response = client.get("/api/v1/patients/9999")

        assert response.status_code == 404


class TestListPatients:
    def test_list_patients_pagination(self, client):
        client.post("/api/v1/patients/", json=_patient_payload())
        client.post(
            "/api/v1/patients/",
            json=_patient_payload(email="jane@example.com", first_name="Jane"),
        )

        response = client.get("/api/v1/patients/")

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 2
        assert len(body["items"]) == 2
        assert "page" in body


class TestUpdatePatient:
    def test_update_patient_success(self, client):
        create = client.post("/api/v1/patients/", json=_patient_payload())
        patient_id = create.json()["id"]

        response = client.put(
            f"/api/v1/patients/{patient_id}",
            json={"first_name": "Johnny"},
        )

        assert response.status_code == 200
        assert response.json()["first_name"] == "Johnny"


class TestDeletePatient:
    def test_soft_delete_patient(self, client):
        create = client.post("/api/v1/patients/", json=_patient_payload())
        patient_id = create.json()["id"]

        response = client.delete(f"/api/v1/patients/{patient_id}")

        assert response.status_code == 200
        assert response.json()["is_active"] is False

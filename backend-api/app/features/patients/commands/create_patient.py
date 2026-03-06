"""
Create Patient Command (CQRS)
"""
from sqlalchemy.orm import Session

from app.common.exceptions import ConflictException
from app.features.patients.models.patient import Patient
from app.features.patients.schemas.patient import PatientCreate


class CreatePatientCommand:
    """Command to create a new patient."""

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, data: PatientCreate) -> Patient:
        existing = self.db.query(Patient).filter(Patient.email == data.email).first()
        if existing:
            raise ConflictException(
                message="Patient already exists",
                detail=f"A patient with email {data.email} already exists",
            )

        patient = Patient(**data.model_dump())

        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient

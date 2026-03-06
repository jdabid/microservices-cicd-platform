"""
Update Patient Command (CQRS)
"""
from sqlalchemy.orm import Session

from app.common.exceptions import ConflictException, NotFoundException
from app.features.patients.models.patient import Patient
from app.features.patients.schemas.patient import PatientUpdate


class UpdatePatientCommand:
    """Command to update an existing patient."""

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, patient_id: int, data: PatientUpdate) -> Patient:
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise NotFoundException(
                message="Patient not found",
                detail=f"Patient with id {patient_id} not found",
            )

        update_data = data.model_dump(exclude_unset=True)

        # Check email uniqueness if changing email
        if "email" in update_data and update_data["email"] != patient.email:
            existing = self.db.query(Patient).filter(Patient.email == update_data["email"]).first()
            if existing:
                raise ConflictException(
                    message="Email already in use",
                    detail=f"A patient with email {update_data['email']} already exists",
                )

        for field, value in update_data.items():
            setattr(patient, field, value)

        self.db.commit()
        self.db.refresh(patient)
        return patient

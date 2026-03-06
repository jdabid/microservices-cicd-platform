"""
Delete Patient Command (CQRS)
Soft-delete by setting is_active=False
"""
from sqlalchemy.orm import Session

from app.common.exceptions import BadRequestException, NotFoundException
from app.features.patients.models.patient import Patient


class DeletePatientCommand:
    """Command to soft-delete a patient."""

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, patient_id: int) -> Patient:
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise NotFoundException(
                message="Patient not found",
                detail=f"Patient with id {patient_id} not found",
            )

        if not patient.is_active:
            raise BadRequestException(
                message="Patient already inactive",
                detail=f"Patient with id {patient_id} is already inactive",
            )

        patient.is_active = False
        self.db.commit()
        self.db.refresh(patient)
        return patient

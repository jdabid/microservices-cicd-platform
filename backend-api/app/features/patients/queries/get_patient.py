"""
Get Patient Query (CQRS)
"""
from sqlalchemy.orm import Session

from app.common.exceptions import NotFoundException
from app.features.patients.models.patient import Patient


class GetPatientQuery:
    """Query to get a single patient by ID."""

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, patient_id: int) -> Patient:
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise NotFoundException(
                message="Patient not found",
                detail=f"Patient with id {patient_id} not found",
            )
        return patient

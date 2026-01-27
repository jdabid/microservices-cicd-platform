"""
Get Appointment Query (CQRS)
Retrieves single appointment - read-only operation
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.features.appointments.models.appointment import Appointment


class GetAppointmentQuery:
    """
    Query to get a single appointment by ID

    CQRS Pattern: This is a QUERY - read-only, no side effects

    Use Cases:
    - View appointment details
    - Check appointment status
    - Display appointment information
    """

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, appointment_id: int) -> Appointment:
        """
        Execute the query to get an appointment

        Args:
            appointment_id: ID of appointment to retrieve

        Returns:
            Appointment object

        Raises:
            HTTPException: If appointment not found
        """
        db_appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()

        if not db_appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Appointment with id {appointment_id} not found"
            )

        return db_appointment
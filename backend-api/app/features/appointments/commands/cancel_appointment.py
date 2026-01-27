"""
Cancel Appointment Command (CQRS)
Handles appointment cancellation - modifies system state
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.features.appointments.models.appointment import Appointment, AppointmentStatus


class CancelAppointmentCommand:
    """
    Command to cancel an appointment

    CQRS Pattern: This is a COMMAND - it modifies system state

    Business Rules:
    - Appointment must exist
    - Appointment must not already be cancelled
    - Cannot cancel completed appointments
    """

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, appointment_id: int) -> Appointment:
        """
        Execute the command to cancel an appointment

        Args:
            appointment_id: ID of appointment to cancel

        Returns:
            Cancelled appointment

        Raises:
            HTTPException: If appointment not found or cannot be cancelled
        """
        # Get existing appointment
        db_appointment = self.db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()

        if not db_appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Appointment with id {appointment_id} not found"
            )

        # Validate business rules
        self._validate_business_rules(db_appointment)

        # Update status to cancelled
        db_appointment.status = AppointmentStatus.CANCELLED

        try:
            self.db.commit()
            self.db.refresh(db_appointment)
            return db_appointment

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cancel appointment: {str(e)}"
            )

    def _validate_business_rules(self, appointment: Appointment) -> None:
        """Validate business rules before cancelling"""
        # Cannot cancel already cancelled appointment
        if appointment.status == AppointmentStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointment is already cancelled"
            )

        # Cannot cancel completed appointment
        if appointment.status == AppointmentStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel a completed appointment"
            )
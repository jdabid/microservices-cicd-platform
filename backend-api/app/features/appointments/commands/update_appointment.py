"""
Update Appointment Command (CQRS)
Handles appointment updates - modifies system state
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.features.appointments.models.appointment import Appointment
from app.features.appointments.schemas.appointment import AppointmentUpdate


class UpdateAppointmentCommand:
    """
    Command to update an existing appointment

    CQRS Pattern: This is a COMMAND - it modifies system state

    Business Rules:
    - Appointment must exist
    - Cannot update cancelled appointments
    - Only provided fields are updated (partial update)
    """

    def __init__(self, db: Session):
        self.db = db

    async def execute(
            self,
            appointment_id: int,
            appointment_data: AppointmentUpdate
    ) -> Appointment:
        """
        Execute the command to update an appointment

        Args:
            appointment_id: ID of appointment to update
            appointment_data: Fields to update (only provided fields)

        Returns:
            Updated appointment

        Raises:
            HTTPException: If appointment not found or cannot be updated
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
        self._validate_business_rules(db_appointment, appointment_data)

        # Update only provided fields
        update_data = appointment_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_appointment, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_appointment)
            return db_appointment

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update appointment: {str(e)}"
            )

    def _validate_business_rules(
            self,
            appointment: Appointment,
            update_data: AppointmentUpdate
    ) -> None:
        """Validate business rules before updating"""
        # Cannot update cancelled appointments
        if appointment.status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update a cancelled appointment"
            )
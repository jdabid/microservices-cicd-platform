"""
Create Appointment Command (CQRS)
Handles appointment creation - modifies system state
"""
from app.tasks.email_tasks import send_appointment_confirmation_email

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.features.appointments.models.appointment import Appointment, AppointmentStatus
from app.features.appointments.schemas.appointment import AppointmentCreate


class CreateAppointmentCommand:
    """
    Command to create a new appointment

    CQRS Pattern: This is a COMMAND - it modifies system state

    Business Rules:
    - Appointment date must be in the future
    - All required fields must be provided
    - Patient email must be valid
    """

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, appointment_data: AppointmentCreate) -> Appointment:
        """
        Execute the command to create an appointment

        Args:
            appointment_data: Validated appointment creation data

        Returns:
            Created appointment with assigned ID

        Raises:
            HTTPException: If validation fails or appointment cannot be created
        """
        # Additional business logic validation
        self._validate_business_rules(appointment_data)

        # Create appointment entity
        db_appointment = Appointment(
            patient_name=appointment_data.patient_name,
            patient_email=appointment_data.patient_email,
            patient_phone=appointment_data.patient_phone,
            doctor_name=appointment_data.doctor_name,
            specialty=appointment_data.specialty,
            appointment_date=appointment_data.appointment_date,
            duration_minutes=appointment_data.duration_minutes,
            reason=appointment_data.reason,
            notes=appointment_data.notes,
            status=AppointmentStatus.SCHEDULED
        )

        try:
            # Persist to database
            self.db.add(db_appointment)
            self.db.commit()
            self.db.refresh(db_appointment)

            # 🆕 Enviar email de confirmación asíncrono
            send_appointment_confirmation_email.delay(
                patient_email=db_appointment.patient_email,
                patient_name=db_appointment.patient_name,
                doctor_name=db_appointment.doctor_name,
                appointment_date=db_appointment.appointment_date.isoformat(),
                appointment_id=db_appointment.id
            )

            return db_appointment

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create appointment: {str(e)}"
            )

    def _validate_business_rules(self, data: AppointmentCreate) -> None:
        """
        Validate business rules before creating appointment

        In a real application, you might check:
        - Doctor availability
        - No overlapping appointments
        - Patient appointment limits
        - etc.
        """
        # Example: Check if appointment is not too far in the future
        max_days_ahead = 90
        days_ahead = (data.appointment_date - datetime.now(data.appointment_date.tzinfo)).days

        if days_ahead > max_days_ahead:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Appointments can only be scheduled up to {max_days_ahead} days in advance"
            )
"""
Appointment Model (SQLAlchemy)
Domain entity for appointments
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Text
from sqlalchemy.sql import func
import enum

from app.common.database.base import Base


class AppointmentStatus(str, enum.Enum):
    """Appointment status enum"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class Appointment(Base):
    """
    Appointment database model

    Represents a medical appointment in the system
    """
    __tablename__ = "appointments"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Patient Information (simplified - en producción serían FK)
    patient_name = Column(String(200), nullable=False, index=True)
    patient_email = Column(String(255), nullable=False)
    patient_phone = Column(String(20), nullable=True)

    # Doctor Information (simplified - en producción serían FK)
    doctor_name = Column(String(200), nullable=False, index=True)
    specialty = Column(String(100), nullable=False)

    # Appointment Details
    appointment_date = Column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes = Column(Integer, default=30)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Status
    status = Column(
        SQLEnum(AppointmentStatus),
        default=AppointmentStatus.SCHEDULED,
        nullable=False,
        index=True
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )

    def __repr__(self):
        return f"<Appointment(id={self.id}, patient={self.patient_name}, date={self.appointment_date}, status={self.status})>"
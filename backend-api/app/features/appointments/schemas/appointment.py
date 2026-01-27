"""
Appointment Schemas (Pydantic)
Data validation and serialization
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator

from app.features.appointments.models.appointment import AppointmentStatus


class AppointmentBase(BaseModel):
    """Base appointment schema with common fields"""
    patient_name: str = Field(..., min_length=2, max_length=200)
    patient_email: EmailStr
    patient_phone: Optional[str] = Field(None, max_length=20)
    doctor_name: str = Field(..., min_length=2, max_length=200)
    specialty: str = Field(..., min_length=2, max_length=100)
    appointment_date: datetime
    duration_minutes: int = Field(default=30, ge=15, le=240)
    reason: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=2000)


class AppointmentCreate(AppointmentBase):
    """
    Schema for creating a new appointment (COMMAND)
    Used in: CreateAppointmentCommand
    """

    @field_validator('appointment_date')
    @classmethod
    def validate_appointment_date(cls, v: datetime) -> datetime:
        """Appointment must be in the future"""
        if v <= datetime.now(v.tzinfo):
            raise ValueError('Appointment date must be in the future')
        return v


class AppointmentUpdate(BaseModel):
    """
    Schema for updating an appointment (COMMAND)
    Used in: UpdateAppointmentCommand
    All fields are optional for partial updates
    """
    patient_name: Optional[str] = Field(None, min_length=2, max_length=200)
    patient_email: Optional[EmailStr] = None
    patient_phone: Optional[str] = Field(None, max_length=20)
    doctor_name: Optional[str] = Field(None, min_length=2, max_length=200)
    specialty: Optional[str] = Field(None, min_length=2, max_length=100)
    appointment_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=240)
    reason: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=2000)
    status: Optional[AppointmentStatus] = None

    @field_validator('appointment_date')
    @classmethod
    def validate_appointment_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Appointment must be in the future if provided"""
        if v is not None and v <= datetime.now(v.tzinfo):
            raise ValueError('Appointment date must be in the future')
        return v


class AppointmentResponse(AppointmentBase):
    """
    Schema for appointment responses (QUERY)
    Used in: GetAppointmentQuery, ListAppointmentsQuery responses
    """
    id: int
    status: AppointmentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Permite crear desde ORM models


class AppointmentListResponse(BaseModel):
    """
    Schema for paginated list responses (QUERY)
    Used in: ListAppointmentsQuery
    """
    items: list[AppointmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
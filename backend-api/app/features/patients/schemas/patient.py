"""
Patient Schemas (Pydantic)
Data validation and serialization
"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.features.patients.models.patient import Gender


class PatientCreate(BaseModel):
    """Schema for creating a new patient (COMMAND)"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    address: Optional[str] = Field(None, max_length=500)


class PatientUpdate(BaseModel):
    """Schema for updating a patient (COMMAND) - partial update"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    address: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class PatientResponse(BaseModel):
    """Schema for patient responses (QUERY)"""
    id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    address: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PatientListResponse(BaseModel):
    """Schema for paginated list responses (QUERY)"""
    items: list[PatientResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

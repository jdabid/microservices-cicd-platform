"""
Appointments Router
FastAPI endpoints that use Commands and Queries (CQRS)
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.common.dependencies.database import get_db
from app.features.appointments.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentListResponse
)
from app.features.appointments.models.appointment import AppointmentStatus
from app.features.appointments.commands.create_appointment import CreateAppointmentCommand
from app.features.appointments.commands.update_appointment import UpdateAppointmentCommand
from app.features.appointments.commands.cancel_appointment import CancelAppointmentCommand
from app.features.appointments.queries.get_appointment import GetAppointmentQuery
from app.features.appointments.queries.list_appointments import (
    ListAppointmentsQuery,
    GetUpcomingAppointmentsQuery,
    GetAppointmentsByPatientQuery,
    GetAppointmentsByDoctorQuery
)

router = APIRouter()


@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Appointment",
    tags=["Commands"]
)
async def create_appointment(
        appointment_data: AppointmentCreate,
        db: Session = Depends(get_db)
):
    """Create a new appointment"""
    command = CreateAppointmentCommand(db)
    return await command.execute(appointment_data)


@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Update Appointment",
    tags=["Commands"]
)
async def update_appointment(
        appointment_id: int,
        appointment_data: AppointmentUpdate,
        db: Session = Depends(get_db)
):
    """Update an existing appointment"""
    command = UpdateAppointmentCommand(db)
    return await command.execute(appointment_id, appointment_data)


@router.delete(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Cancel Appointment",
    tags=["Commands"]
)
async def cancel_appointment(
        appointment_id: int,
        db: Session = Depends(get_db)
):
    """Cancel an appointment"""
    command = CancelAppointmentCommand(db)
    return await command.execute(appointment_id)


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Get Appointment",
    tags=["Queries"]
)
async def get_appointment(
        appointment_id: int,
        db: Session = Depends(get_db)
):
    """Get a single appointment by ID"""
    query = GetAppointmentQuery(db)
    return await query.execute(appointment_id)


@router.get(
    "/",
    response_model=AppointmentListResponse,
    summary="List Appointments",
    tags=["Queries"]
)
async def list_appointments(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        status: Optional[AppointmentStatus] = Query(None),
        patient_name: Optional[str] = Query(None),
        doctor_name: Optional[str] = Query(None),
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None),
        db: Session = Depends(get_db)
):
    """List appointments with pagination and filtering"""
    query = ListAppointmentsQuery(db)
    result = await query.execute(
        page=page,
        page_size=page_size,
        status=status,
        patient_name=patient_name,
        doctor_name=doctor_name,
        start_date=start_date,
        end_date=end_date
    )

    return AppointmentListResponse(
        items=[AppointmentResponse.model_validate(item) for item in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"]
    )


@router.get(
    "/upcoming/next-days",
    response_model=list[AppointmentResponse],
    summary="Get Upcoming Appointments",
    tags=["Queries"]
)
async def get_upcoming_appointments(
        days_ahead: int = Query(7, ge=1, le=90),
        db: Session = Depends(get_db)
):
    """Get appointments scheduled in the next N days"""
    query = GetUpcomingAppointmentsQuery(db)
    appointments = await query.execute(days_ahead)
    return [AppointmentResponse.model_validate(apt) for apt in appointments]


@router.get(
    "/patient/{patient_email}",
    response_model=list[AppointmentResponse],
    summary="Get Patient Appointments",
    tags=["Queries"]
)
async def get_patient_appointments(
        patient_email: str,
        db: Session = Depends(get_db)
):
    """Get all appointments for a specific patient"""
    query = GetAppointmentsByPatientQuery(db)
    appointments = await query.execute(patient_email)
    return [AppointmentResponse.model_validate(apt) for apt in appointments]


@router.get(
    "/doctor/{doctor_name}",
    response_model=list[AppointmentResponse],
    summary="Get Doctor Appointments",
    tags=["Queries"]
)
async def get_doctor_appointments(
        doctor_name: str,
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None),
        db: Session = Depends(get_db)
):
    """Get all appointments for a specific doctor"""
    query = GetAppointmentsByDoctorQuery(db)
    appointments = await query.execute(doctor_name, start_date, end_date)
    return [AppointmentResponse.model_validate(apt) for apt in appointments]
"""
List Appointments Query (CQRS)
Retrieves multiple appointments with filtering and pagination - read-only
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime
from math import ceil

from app.features.appointments.models.appointment import Appointment, AppointmentStatus


class ListAppointmentsQuery:
    """
    Query to list appointments with pagination and filtering

    CQRS Pattern: This is a QUERY - read-only, no side effects

    Features:
    - Pagination (page and page_size)
    - Filter by status
    - Filter by patient name (search)
    - Filter by doctor name (search)
    - Filter by date range
    - Sorting by appointment_date
    """

    def __init__(self, db: Session):
        self.db = db

    async def execute(
            self,
            skip: int = 0,
            limit: int = 100,
            status: Optional[AppointmentStatus] = None,
            patient_name: Optional[str] = None,
            doctor_name: Optional[str] = None,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            page: int = 1,
            page_size: int = 20
    ) -> dict:
        """
        Execute the query to list appointments

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            status: Filter by appointment status
            patient_name: Search by patient name (partial match)
            doctor_name: Search by doctor name (partial match)
            start_date: Filter appointments from this date
            end_date: Filter appointments until this date
            page: Page number (starts at 1)
            page_size: Items per page

        Returns:
            Dictionary with:
            - items: List of appointments
            - total: Total count of matching appointments
            - page: Current page
            - page_size: Items per page
            - total_pages: Total number of pages
        """
        # Build base query
        query = self.db.query(Appointment)

        # Apply filters
        filters = []

        if status:
            filters.append(Appointment.status == status)

        if patient_name:
            filters.append(Appointment.patient_name.ilike(f"%{patient_name}%"))

        if doctor_name:
            filters.append(Appointment.doctor_name.ilike(f"%{doctor_name}%"))

        if start_date:
            filters.append(Appointment.appointment_date >= start_date)

        if end_date:
            filters.append(Appointment.appointment_date <= end_date)

        # Apply all filters
        if filters:
            query = query.filter(and_(*filters))

        # Get total count before pagination
        total = query.count()

        # Apply sorting (most recent first)
        query = query.order_by(Appointment.appointment_date.asc())

        # Apply pagination
        # Calculate skip from page number
        calculated_skip = (page - 1) * page_size

        appointments = query.offset(calculated_skip).limit(page_size).all()

        # Calculate total pages
        total_pages = ceil(total / page_size) if page_size > 0 else 0

        return {
            "items": appointments,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }


class GetUpcomingAppointmentsQuery:
    """
    Query to get upcoming appointments for a specific time range

    Useful for dashboard views
    """

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, days_ahead: int = 7) -> list[Appointment]:
        """
        Get appointments scheduled in the next N days

        Args:
            days_ahead: Number of days to look ahead

        Returns:
            List of upcoming appointments
        """
        from datetime import timedelta

        now = datetime.now()
        future_date = now + timedelta(days=days_ahead)

        appointments = self.db.query(Appointment).filter(
            and_(
                Appointment.appointment_date >= now,
                Appointment.appointment_date <= future_date,
                Appointment.status.in_([
                    AppointmentStatus.SCHEDULED,
                    AppointmentStatus.CONFIRMED
                ])
            )
        ).order_by(Appointment.appointment_date.asc()).all()

        return appointments


class GetAppointmentsByPatientQuery:
    """
    Query to get all appointments for a specific patient

    Useful for patient history
    """

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, patient_email: str) -> list[Appointment]:
        """
        Get all appointments for a patient by email

        Args:
            patient_email: Patient's email address

        Returns:
            List of patient's appointments
        """
        appointments = self.db.query(Appointment).filter(
            Appointment.patient_email == patient_email
        ).order_by(Appointment.appointment_date.desc()).all()

        return appointments


class GetAppointmentsByDoctorQuery:
    """
    Query to get all appointments for a specific doctor

    Useful for doctor's schedule
    """

    def __init__(self, db: Session):
        self.db = db

    async def execute(
            self,
            doctor_name: str,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None
    ) -> list[Appointment]:
        """
        Get all appointments for a doctor

        Args:
            doctor_name: Doctor's name
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of doctor's appointments
        """
        query = self.db.query(Appointment).filter(
            Appointment.doctor_name == doctor_name
        )

        if start_date:
            query = query.filter(Appointment.appointment_date >= start_date)

        if end_date:
            query = query.filter(Appointment.appointment_date <= end_date)

        appointments = query.order_by(
            Appointment.appointment_date.asc()
        ).all()

        return appointments
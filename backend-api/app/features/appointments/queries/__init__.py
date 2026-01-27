"""
Appointments Queries (CQRS Read Operations)
"""
from app.features.appointments.queries.get_appointment import GetAppointmentQuery
from app.features.appointments.queries.list_appointments import (
    ListAppointmentsQuery,
    GetUpcomingAppointmentsQuery,
    GetAppointmentsByPatientQuery,
    GetAppointmentsByDoctorQuery
)

__all__ = [
    "GetAppointmentQuery",
    "ListAppointmentsQuery",
    "GetUpcomingAppointmentsQuery",
    "GetAppointmentsByPatientQuery",
    "GetAppointmentsByDoctorQuery"
]
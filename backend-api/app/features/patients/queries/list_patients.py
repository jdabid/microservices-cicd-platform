"""
List Patients Query (CQRS)
"""
from math import ceil
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.features.patients.models.patient import Patient


class ListPatientsQuery:
    """Query to list patients with pagination and filtering."""

    def __init__(self, db: Session):
        self.db = db

    async def execute(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> dict:
        query = self.db.query(Patient)

        filters = []
        if search:
            pattern = f"%{search}%"
            filters.append(
                Patient.first_name.ilike(pattern)
                | Patient.last_name.ilike(pattern)
                | Patient.email.ilike(pattern)
            )
        if is_active is not None:
            filters.append(Patient.is_active == is_active)

        if filters:
            query = query.filter(and_(*filters))

        total = query.count()
        skip = (page - 1) * page_size
        patients = query.order_by(Patient.last_name.asc()).offset(skip).limit(page_size).all()
        total_pages = ceil(total / page_size) if page_size > 0 else 0

        return {
            "items": patients,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

"""
Patients Router
FastAPI endpoints that use Commands and Queries (CQRS)
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.common.dependencies.database import get_db
from app.features.patients.commands.create_patient import CreatePatientCommand
from app.features.patients.commands.delete_patient import DeletePatientCommand
from app.features.patients.commands.update_patient import UpdatePatientCommand
from app.features.patients.queries.get_patient import GetPatientQuery
from app.features.patients.queries.list_patients import ListPatientsQuery
from app.features.patients.schemas.patient import (
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)

router = APIRouter()


@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Patient",
    tags=["Commands"],
)
async def create_patient(
    data: PatientCreate,
    db: Session = Depends(get_db),
) -> PatientResponse:
    """Create a new patient record."""
    command = CreatePatientCommand(db)
    patient = await command.execute(data)
    return PatientResponse.model_validate(patient)


@router.get(
    "/",
    response_model=PatientListResponse,
    summary="List Patients",
    tags=["Queries"],
)
async def list_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
) -> PatientListResponse:
    """List patients with pagination and search."""
    query = ListPatientsQuery(db)
    result = await query.execute(
        page=page, page_size=page_size, search=search, is_active=is_active
    )
    return PatientListResponse(
        items=[PatientResponse.model_validate(p) for p in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"],
    )


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Get Patient",
    tags=["Queries"],
)
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
) -> PatientResponse:
    """Get a single patient by ID."""
    query = GetPatientQuery(db)
    patient = await query.execute(patient_id)
    return PatientResponse.model_validate(patient)


@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Update Patient",
    tags=["Commands"],
)
async def update_patient(
    patient_id: int,
    data: PatientUpdate,
    db: Session = Depends(get_db),
) -> PatientResponse:
    """Update an existing patient."""
    command = UpdatePatientCommand(db)
    patient = await command.execute(patient_id, data)
    return PatientResponse.model_validate(patient)


@router.delete(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Delete Patient",
    tags=["Commands"],
)
async def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
) -> PatientResponse:
    """Soft-delete a patient (set inactive)."""
    command = DeletePatientCommand(db)
    patient = await command.execute(patient_id)
    return PatientResponse.model_validate(patient)

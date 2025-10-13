from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.patient import Patient
from app.models.staff import Staff
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate
from app.api.api_v1.endpoints.auth import get_current_staff
import uuid

router = APIRouter()

@router.post("/", response_model=PatientResponse)
def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    db_patient = Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    try:
        patient_uuid = uuid.UUID(patient_id) if not isinstance(patient_id, uuid.UUID) else patient_id
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    patient = db.query(Patient).filter(Patient.id == patient_uuid).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    return patient

@router.get("/", response_model=List[PatientResponse])
def search_patients(
    query: Optional[str] = Query(None, description="Search by name, email, or phone"),
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    patients_query = db.query(Patient)
    
    if query:
        patients_query = patients_query.filter(
            Patient.name.ilike(f"%{query}%") |
            Patient.email.ilike(f"%{query}%") |
            Patient.phone.ilike(f"%{query}%")
        )
    
    return patients_query.all()

@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: str,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    try:
        patient_uuid = uuid.UUID(patient_id) if not isinstance(patient_id, uuid.UUID) else patient_id
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    patient = db.query(Patient).filter(Patient.id == patient_uuid).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    update_data = patient_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{patient_id}")
def delete_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    try:
        patient_uuid = uuid.UUID(patient_id) if not isinstance(patient_id, uuid.UUID) else patient_id
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    patient = db.query(Patient).filter(Patient.id == patient_uuid).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    # Simple delete; if invoices exist you'd normally soft-delete or prevent deletion
    db.delete(patient)
    db.commit()
    return {"detail": "Patient deleted"}

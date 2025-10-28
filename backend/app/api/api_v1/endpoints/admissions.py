"""
Admission API endpoints for patient admission and discharge workflow.

This module provides REST endpoints for admission management including
patient admission, discharge, and billing operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.admission import (
    Admission, AdmissionCreate, AdmissionUpdate, AdmissionListResponse,
    DischargeRequest, DischargeResponse, AdmissionFilter
)
from app.models.admission import AdmissionStatus
from app.services.admission_service import AdmissionService
from app.models.room import Room
from app.core.auth import (
    get_current_user, require_permission, require_admission_creation,
    Permission, User
)
from app.utils.id_mapping import map_request_ids

router = APIRouter()


@router.get("/", response_model=AdmissionListResponse)
def get_admissions(
    status: Optional[str] = Query(None, description="Filter by admission status"),
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    active_only: bool = Query(False, description="Show only active admissions"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get admissions with optional filtering.
    
    Args:
        status: Optional admission status filter
        patient_id: Optional patient ID filter
        room_id: Optional room ID filter
        active_only: Show only active admissions
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of admissions with total count
    """
    try:
        # Create filter object
        filters = AdmissionFilter(
            status=status,
            patient_id=patient_id,
            room_id=room_id,
            active_only=active_only
        )
        
        # Get admissions and count
        admission_service = AdmissionService(db)
        admissions = admission_service.get_admissions(
            patient_id=filters.patient_id,
            room_id=filters.room_id,
            status=filters.status,
            skip=skip,
            limit=limit
        )
        total = admission_service.get_admission_count(
            patient_id=filters.patient_id,
            room_id=filters.room_id,
            status=filters.status
        )
        
        return AdmissionListResponse(
            admissions=admissions,
            total=total,
            page=skip // limit + 1,
            size=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving admissions: {str(e)}")


@router.get("/{admission_id}", response_model=Admission)
def get_admission(admission_id: int, db: Session = Depends(get_db)):
    """
    Get admission by ID.
    
    Args:
        admission_id: Admission ID
        db: Database session
        
    Returns:
        Admission details
        
    Raises:
        HTTPException: If admission not found
    """
    admission_service = AdmissionService(db)
    admission = admission_service.get_admission(admission_id)
    
    if not admission:
        raise HTTPException(status_code=404, detail="Admission not found")
    
    return admission


@router.post("/", response_model=Admission, status_code=201)
def create_admission(
    admission_data: AdmissionCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.CREATE_ADMISSIONS))
):
    """
    Create a new admission.
    
    Args:
        admission_data: Admission creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created admission details
        
    Raises:
        HTTPException: If room not available, patient already admitted, or validation fails
    """
    try:
        admission_service = AdmissionService(db)
        
        # Pre-validate all components before attempting creation
        room_service = db.query(Room).filter(Room.id == admission_data.room_id).first()
        if not room_service:
            raise HTTPException(status_code=400, detail=f"Room with ID {admission_data.room_id} not found")
        
        # Check room availability
        room_availability = admission_service.validate_room_availability(admission_data.room_id)
        if not room_availability.get('available', False):
            raise HTTPException(status_code=400, detail=room_availability.get('reason', 'Room not available'))
        
        # Check patient eligibility
        patient_eligibility = admission_service.check_patient_eligibility(admission_data.patient_id)
        if not patient_eligibility.get('eligible', False):
            raise HTTPException(status_code=400, detail=patient_eligibility.get('reason', 'Patient not eligible'))
        
        # Check staff authorization
        staff_authorization = admission_service.check_staff_authorization(admission_data.staff_id)
        if not staff_authorization.get('authorized', False):
            raise HTTPException(status_code=400, detail=staff_authorization.get('reason', 'Staff not authorized'))
        
        # Create admission - this should not fail validation errors since we pre-validated
        admission = admission_service.create_admission(admission_data)
        return admission
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating admission: {str(e)}")


@router.put("/{admission_id}", response_model=Admission)
def update_admission(admission_id: int, admission_data: AdmissionUpdate, db: Session = Depends(get_db)):
    """
    Update admission details.
    
    Args:
        admission_id: Admission ID
        admission_data: Admission update data
        db: Database session
        
    Returns:
        Updated admission details
        
    Raises:
        HTTPException: If admission not found
    """
    try:
        admission_service = AdmissionService(db)
        admission = admission_service.update_admission(admission_id, admission_data)
        
        if not admission:
            raise HTTPException(status_code=404, detail="Admission not found")
        
        return admission
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating admission: {str(e)}")


@router.post("/{admission_id}/discharge", response_model=DischargeResponse)
def discharge_patient(admission_id: int, discharge_data: DischargeRequest, db: Session = Depends(get_db)):
    """
    Discharge a patient and calculate billing.
    
    Args:
        admission_id: Admission ID
        discharge_data: Discharge request data
        db: Database session
        
    Returns:
        Discharge response with admission, invoice, and billing summary
        
    Raises:
        HTTPException: If admission not found or cannot be discharged
    """
    try:
        admission_service = AdmissionService(db)
        result = admission_service.discharge_patient(admission_id, discharge_data)
        
        return DischargeResponse(
            admission=result['admission'],
            invoice=result['invoice'],
            billing_summary=result['billing_summary']
        )
    except ValueError as e:
        # Provide more specific error messages for common validation issues
        error_message = str(e)
        if "Discharge date cannot be more than" in error_message:
            raise HTTPException(status_code=400, detail=f"Invalid discharge date: {error_message}")
        elif "Admission with ID" in error_message and "not found" in error_message:
            raise HTTPException(status_code=404, detail=f"Admission not found: {error_message}")
        elif "cannot be discharged" in error_message:
            raise HTTPException(status_code=400, detail=f"Cannot discharge patient: {error_message}")
        else:
            raise HTTPException(status_code=400, detail=f"Validation error: {error_message}")
    except Exception as e:
        # Log the full error for debugging
        import logging
        logging.error(f"Error discharging patient {admission_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error discharging patient: {str(e)}")


@router.get("/active/list", response_model=List[Admission])
def get_active_admissions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    room_id: Optional[int] = Query(None, description="Filter by room ID"),
    db: Session = Depends(get_db)
):
    """
    Get active admissions with optional filtering.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        patient_id: Optional patient ID filter
        room_id: Optional room ID filter
        db: Database session

    Returns:
        List of active admissions
    """
    try:
        admission_service = AdmissionService(db)
        admissions = admission_service.get_admissions(
            patient_id=patient_id,
            room_id=room_id,
            status=AdmissionStatus.ACTIVE,
            skip=skip,
            limit=limit
        )
        return admissions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving active admissions: {str(e)}")


@router.get("/active/statistics")
def get_active_admissions_statistics(db: Session = Depends(get_db)):
    """
    Get statistics for active admissions.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with admission statistics
    """
    try:
        admission_service = AdmissionService(db)
        stats = admission_service.get_admission_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving admission statistics: {str(e)}")


@router.get("/patient/{patient_id}", response_model=List[Admission])
def get_patient_admissions(
    patient_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get admissions for a specific patient.
    
    Args:
        patient_id: Patient ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of patient admissions
    """
    try:
        admission_service = AdmissionService(db)
        admissions = admission_service.get_admissions(patient_id=patient_id, skip=skip, limit=limit)
        return admissions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving patient admissions: {str(e)}")


@router.get("/room/{room_id}", response_model=List[Admission])
def get_room_admissions(
    room_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get admissions for a specific room.
    
    Args:
        room_id: Room ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of room admissions
    """
    try:
        admission_service = AdmissionService(db)
        admissions = admission_service.get_admissions(room_id=room_id, skip=skip, limit=limit)
        return admissions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving room admissions: {str(e)}")



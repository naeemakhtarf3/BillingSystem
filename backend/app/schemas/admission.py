"""
Pydantic schemas for Admission entity validation and serialization.

This module defines the request/response schemas for admission operations
with proper validation and type safety.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Union
from datetime import datetime
from enum import Enum

from app.models.admission import AdmissionStatus


class AdmissionBase(BaseModel):
    """Base admission schema with common fields."""
    room_id: int = Field(..., description="Room ID")
    patient_id: Union[int, str] = Field(..., description="Patient ID (integer or UUID string)")
    staff_id: Union[int, str] = Field(..., description="Staff ID (integer or UUID string)")
    admission_date: datetime = Field(..., description="Admission date")
    
    @validator('patient_id')
    def validate_patient_id(cls, v):
        """Convert integer patient ID to UUID if needed."""
        if isinstance(v, int):
            from app.utils.id_mapping import get_patient_uuid_by_id
            uuid = get_patient_uuid_by_id(v)
            if not uuid:
                raise ValueError(f'Patient ID {v} not found')
            return uuid
        return v
    
    @validator('staff_id')
    def validate_staff_id(cls, v):
        """Convert integer staff ID to UUID if needed."""
        if isinstance(v, int):
            from app.utils.id_mapping import get_staff_uuid_by_id
            uuid = get_staff_uuid_by_id(v)
            if not uuid:
                raise ValueError(f'Staff ID {v} not found')
            return uuid
        return v
    
    @validator('admission_date')
    def validate_admission_date(cls, v):
        """Validate admission date is reasonable."""
        from datetime import datetime, timezone, timedelta
        
        # Ensure both datetimes are timezone-aware for comparison
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        
        # Allow dates up to 2 years in the future
        max_future = now + timedelta(days=730)
        if v > max_future:
            raise ValueError('Admission date cannot be more than 2 years in the future')
        
        # Allow dates up to 10 years in the past
        max_past = now - timedelta(days=3650)
        if v < max_past:
            raise ValueError('Admission date cannot be more than 10 years in the past')
        
        return v


class AdmissionCreate(AdmissionBase):
    """Schema for creating a new admission."""
    pass


class AdmissionUpdate(BaseModel):
    """Schema for updating admission details."""
    discharge_date: Optional[datetime] = Field(None, description="Discharge date")
    
    @validator('discharge_date')
    def validate_discharge_date(cls, v, values):
        """Validate discharge date is after admission date."""
        if v and 'admission_date' in values and v <= values['admission_date']:
            raise ValueError('Discharge date must be after admission date')
        return v


class DischargeRequest(BaseModel):
    """Schema for discharge request."""
    discharge_date: datetime = Field(..., description="Discharge date")
    discharge_reason: Optional[str] = Field(None, description="Reason for discharge")
    discharge_notes: Optional[str] = Field(None, description="Additional discharge notes")
    
    @validator('discharge_date')
    def validate_discharge_date(cls, v):
        """Validate discharge date is reasonable."""
        from datetime import timedelta, timezone
        
        # Ensure both datetimes are timezone-aware for comparison
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        
        # Allow discharge dates up to 1 year in the future (for planned discharges and testing)
        max_future = now + timedelta(days=365)
        if v > max_future:
            raise ValueError('Discharge date cannot be more than 1 year in the future')
        
        # Allow discharge dates up to 1 year in the past
        max_past = now - timedelta(days=365)
        if v < max_past:
            raise ValueError('Discharge date cannot be more than 1 year in the past')
        
        return v
    
    @validator('discharge_reason')
    def validate_discharge_reason(cls, v):
        """Validate discharge reason if provided."""
        if v:
            valid_reasons = ['recovery', 'transfer', 'patient_request', 'medical_necessity', 'other']
            if v not in valid_reasons:
                raise ValueError(f"Invalid discharge reason. Must be one of: {', '.join(valid_reasons)}")
        return v
    
    @validator('discharge_notes')
    def validate_discharge_notes(cls, v):
        """Validate discharge notes if provided."""
        if v and len(v) > 500:
            raise ValueError("Discharge notes cannot exceed 500 characters")
        return v


class AdmissionInDBBase(AdmissionBase):
    """Base schema for admission in database."""
    id: int
    discharge_date: Optional[datetime]
    discharge_reason: Optional[str]
    discharge_notes: Optional[str]
    invoice_id: Optional[int] = Field(None, description="Invoice ID")
    status: AdmissionStatus
    created_at: datetime
    updated_at: datetime
    version: int = Field(default=1, description="Optimistic locking version")
    
    @validator('invoice_id', pre=True)
    def validate_invoice_id(cls, v):
        """Handle invoice_id as either integer or string, converting to int."""
        if v is None:
            return None
        # If it's already an integer, return as is
        if isinstance(v, int):
            return v
        # If it's a string, try to convert to int
        if isinstance(v, str):
            # Try to extract numeric part if it's in format like "INV-1-123456"
            if v.startswith('INV-'):
                try:
                    # Extract the numeric part after the last dash
                    parts = v.split('-')
                    if len(parts) > 1:
                        numeric_part = parts[-1]
                        return int(numeric_part)
                except (ValueError, IndexError):
                    pass
            # Try direct conversion
            try:
                return int(v)
            except ValueError:
                # If conversion fails, return None to avoid validation errors
                return None
        return v
    
    class Config:
        from_attributes = True


class Admission(AdmissionInDBBase):
    """Schema for admission response."""
    pass


class AdmissionWithDetails(Admission):
    """Schema for admission response with related details."""
    room_number: Optional[str] = Field(None, description="Room number")
    patient_name: Optional[str] = Field(None, description="Patient name")
    staff_name: Optional[str] = Field(None, description="Staff name")
    daily_rate_cents: Optional[int] = Field(None, description="Room daily rate")


class AdmissionFilter(BaseModel):
    """Schema for admission filtering."""
    status: Optional[AdmissionStatus] = Field(None, description="Filter by admission status")
    patient_id: Optional[str] = Field(None, description="Filter by patient ID")
    room_id: Optional[int] = Field(None, description="Filter by room ID")
    active_only: Optional[bool] = Field(False, description="Show only active admissions")


class AdmissionListResponse(BaseModel):
    """Schema for admission list response."""
    admissions: list[AdmissionWithDetails] = Field(..., description="List of admissions")
    total: int = Field(..., description="Total number of admissions")
    page: int = Field(1, description="Current page number")
    size: int = Field(10, description="Page size")


class BillingSummary(BaseModel):
    """Schema for billing summary."""
    daily_rate_cents: int = Field(..., description="Daily rate in cents")
    days_stayed: float = Field(..., description="Number of days stayed")
    total_charges_cents: int = Field(..., description="Total charges in cents")
    is_same_day: bool = Field(..., description="Whether admission and discharge are same day")


class DischargeResponse(BaseModel):
    """Schema for discharge response."""
    admission: Admission = Field(..., description="Updated admission")
    invoice: dict = Field(..., description="Generated invoice details")
    billing_summary: BillingSummary = Field(..., description="Billing calculation summary")

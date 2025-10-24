"""
Pydantic schemas for Admission entity validation and serialization.

This module defines the request/response schemas for admission operations
with proper validation and type safety.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

from app.models.admission import AdmissionStatus


class AdmissionBase(BaseModel):
    """Base admission schema with common fields."""
    room_id: int = Field(..., description="Room ID")
    patient_id: int = Field(..., description="Patient ID")
    staff_id: int = Field(..., description="Staff ID who processed admission")
    admission_date: datetime = Field(..., description="Admission date")
    
    @validator('admission_date')
    def validate_admission_date(cls, v):
        """Validate admission date is not in the future."""
        if v > datetime.now():
            raise ValueError('Admission date cannot be in the future')
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
    
    @validator('discharge_date')
    def validate_discharge_date(cls, v):
        """Validate discharge date is not in the future."""
        if v > datetime.now():
            raise ValueError('Discharge date cannot be in the future')
        return v


class AdmissionInDBBase(AdmissionBase):
    """Base schema for admission in database."""
    id: int
    discharge_date: Optional[datetime]
    invoice_id: Optional[int]
    status: AdmissionStatus
    created_at: datetime
    updated_at: datetime
    
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
    patient_id: Optional[int] = Field(None, description="Filter by patient ID")
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

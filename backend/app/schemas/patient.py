from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, date
import uuid

class PatientCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[date] = None
    patient_metadata: Optional[Dict[str, Any]] = None

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[date] = None
    patient_metadata: Optional[Dict[str, Any]] = None

class PatientResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[date] = None
    patient_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

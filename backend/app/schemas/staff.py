from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
from app.models.staff import StaffRole

class StaffCreate(BaseModel):
    email: str
    password: str
    name: str
    role: StaffRole = StaffRole.BILLING_CLERK

class StaffLogin(BaseModel):
    email: str
    password: str

class StaffResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: StaffRole
    created_at: datetime
    
    class Config:
        from_attributes = True

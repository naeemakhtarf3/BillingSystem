from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.payment import PaymentStatus


class PaymentCreate(BaseModel):
    invoice_id: str
    amount_cents: int
    currency: str
    method: Optional[str] = 'cash'
    note: Optional[str] = None
    received_at: Optional[datetime] = None


class PaymentResponse(BaseModel):
    id: str
    invoice_id: str
    stripe_payment_id: Optional[str] = None
    amount_cents: int
    currency: str
    status: PaymentStatus
    received_at: Optional[datetime] = None
    raw_event: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class PaymentListItem(BaseModel):
    id: str
    invoice_id: str
    invoice_number: Optional[str] = None
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    patient_email: Optional[str] = None
    stripe_payment_id: Optional[str] = None
    amount_cents: int
    currency: str
    status: PaymentStatus
    received_at: Optional[datetime] = None

    class Config:
        from_attributes = True

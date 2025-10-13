from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
import uuid
from app.models.invoice import InvoiceStatus

class InvoiceItemCreate(BaseModel):
    description: str
    quantity: int = 1
    unit_price_cents: int
    tax_cents: int = 0

class InvoiceItemResponse(BaseModel):
    id: uuid.UUID
    description: str
    quantity: int
    unit_price_cents: int
    tax_cents: int
    
    class Config:
        from_attributes = True

class InvoiceCreate(BaseModel):
    patient_id: uuid.UUID
    currency: str = "USD"
    due_date: Optional[date] = None
    payment_method: Optional[str] = None
    items: List[InvoiceItemCreate]

class InvoiceResponse(BaseModel):
    id: uuid.UUID
    invoice_number: str
    patient_id: uuid.UUID
    staff_id: uuid.UUID
    currency: str
    payment_method: Optional[str] = None
    total_amount_cents: int
    status: InvoiceStatus
    issued_at: Optional[datetime] = None
    due_date: Optional[date] = None
    stripe_payment_link_id: Optional[str] = None
    stripe_checkout_session_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[InvoiceItemResponse] = []
    
    class Config:
        from_attributes = True

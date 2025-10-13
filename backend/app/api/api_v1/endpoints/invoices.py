from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from app.db.session import get_db
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus
from app.models.patient import Patient
from app.models.staff import Staff
from app.schemas.invoice import InvoiceCreate, InvoiceResponse
from app.api.api_v1.endpoints.auth import get_current_staff
import uuid

router = APIRouter()

def generate_invoice_number(db: Session) -> str:
    """Generate unique invoice number in format CLINIC-YYYYMM-0001"""
    from datetime import datetime
    current_date = datetime.now()
    year_month = current_date.strftime("%Y%m")
    
    # Find the highest invoice number for this month
    last_invoice = db.query(Invoice).filter(
        Invoice.invoice_number.like(f"CLINIC-{year_month}-%")
    ).order_by(Invoice.invoice_number.desc()).first()
    
    if last_invoice:
        # Extract the sequence number and increment
        sequence = int(last_invoice.invoice_number.split("-")[-1]) + 1
    else:
        sequence = 1
    
    return f"CLINIC-{year_month}-{sequence:04d}"

@router.post("/", response_model=InvoiceResponse)
def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == invoice.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Calculate total amount
    total_amount_cents = sum(
        (item.quantity * item.unit_price_cents) + item.tax_cents
        for item in invoice.items
    )
    
    # Create invoice
    db_invoice = Invoice(
        invoice_number=generate_invoice_number(db),
        patient_id=invoice.patient_id,
        staff_id=current_staff.id,
        currency=invoice.currency,
        total_amount_cents=total_amount_cents,
        due_date=invoice.due_date
    )
    
    db.add(db_invoice)
    db.flush()  # Get the invoice ID
    
    # Create invoice items
    for item in invoice.items:
        db_item = InvoiceItem(
            invoice_id=db_invoice.id,
            description=item.description,
            quantity=item.quantity,
            unit_price_cents=item.unit_price_cents,
            tax_cents=item.tax_cents
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_invoice)
    # Persist payment_method if provided and model has attribute
    try:
        if getattr(db_invoice, 'payment_method', None) is not None and invoice.payment_method:
            db_invoice.payment_method = invoice.payment_method
            db.commit()
            db.refresh(db_invoice)
    except Exception:
        # ignore if DB schema doesn't have this column yet
        pass
    return db_invoice

@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    try:
        invoice_uuid = uuid.UUID(invoice_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invoice id")

    invoice = db.query(Invoice).filter(Invoice.id == invoice_uuid).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    return invoice

@router.get("/", response_model=List[InvoiceResponse])
def list_invoices(
    patient_id: Optional[str] = Query(None),
    status: Optional[InvoiceStatus] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    query = db.query(Invoice)
    
    if patient_id:
        try:
            pid = uuid.UUID(patient_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid patient id")
        query = query.filter(Invoice.patient_id == pid)
    if status:
        query = query.filter(Invoice.status == status)
    if from_date:
        query = query.filter(Invoice.created_at >= from_date)
    if to_date:
        query = query.filter(Invoice.created_at <= to_date)
    
    return query.order_by(Invoice.created_at.desc()).all()

@router.post("/{invoice_id}/issue", response_model=InvoiceResponse)
def issue_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    try:
        invoice_uuid = uuid.UUID(invoice_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invoice id")

    invoice = db.query(Invoice).filter(Invoice.id == invoice_uuid).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    if invoice.status != InvoiceStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice is not in draft status"
        )
    
    # Update invoice status and issue date
    invoice.status = InvoiceStatus.ISSUED
    invoice.issued_at = datetime.utcnow()
    
    db.commit()
    db.refresh(invoice)
    return invoice

@router.post("/{invoice_id}/cancel", response_model=InvoiceResponse)
def cancel_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    try:
        invoice_uuid = uuid.UUID(invoice_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invoice id")

    invoice = db.query(Invoice).filter(Invoice.id == invoice_uuid).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    if invoice.status in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel paid or already cancelled invoice"
        )
    
    invoice.status = InvoiceStatus.CANCELLED
    db.commit()
    db.refresh(invoice)
    return invoice

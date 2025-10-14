# Simplified clinic agent without ADK dependencies
# This will work with your existing setup
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import json

# Import your existing models and services
from app.models.patient import Patient
from app.models.invoice import Invoice, InvoiceItem
from app.models.payment import Payment
from app.db.session import get_db
from sqlalchemy.orm import Session as SQLSession
from sqlalchemy import func

# Set up Google API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyDi0QD7_-N7JJFXm5B6wbhkXXJdnT_hKZo"

# Tool to get patient information
def get_patient_info(patient_id: int) -> Dict[str, Any]:
    """Get detailed information about a patient by ID."""
    db = next(get_db())
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            return {"error": f"Patient with ID {patient_id} not found"}
        
        # Get related invoices and payments
        invoices = db.query(Invoice).filter(Invoice.patient_id == patient_id).all()
        payments = db.query(Payment).filter(Payment.patient_id == patient_id).all()
        
        return {
            "patient": {
                "id": patient.id,
                "name": patient.name,
                "email": patient.email,
                "phone": patient.phone,
                "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                "address": patient.address,
                "created_at": patient.created_at.isoformat() if patient.created_at else None
            },
            "invoices": [
                {
                    "id": invoice.id,
                    "amount": float(invoice.amount),
                    "status": invoice.status,
                    "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                    "created_at": invoice.created_at.isoformat() if invoice.created_at else None
                } for invoice in invoices
            ],
            "payments": [
                {
                    "id": payment.id,
                    "amount": float(payment.amount),
                    "status": payment.status,
                    "payment_method": payment.payment_method,
                    "created_at": payment.created_at.isoformat() if payment.created_at else None
                } for payment in payments
            ]
        }
    finally:
        db.close()

# Tool to search patients by name or email test
def search_patients(query: str) -> List[Dict[str, Any]]:
    """Search for patients by name or email."""
    db = next(get_db())
    try:
        patients = db.query(Patient).filter(
            (Patient.name.ilike(f"%{query}%")) | 
            (Patient.email.ilike(f"%{query}%"))
        ).limit(10).all()
        
        return [
            {
                "id": patient.id,
                "name": patient.name,
                "email": patient.email,
                "phone": patient.phone,
                "created_at": patient.created_at.isoformat() if patient.created_at else None
            } for patient in patients
        ]
    finally:
        db.close()

# Tool to get billing summary
def get_billing_summary() -> Dict[str, Any]:
    """Get overall billing summary including total revenue, outstanding amounts, etc."""
    db = next(get_db())
    try:
        # Get total patients
        total_patients = db.query(func.count(Patient.id)).scalar()
        
        # Get total invoices and amounts
        total_invoices = db.query(func.count(Invoice.id)).scalar()
        total_invoice_amount = db.query(func.sum(Invoice.amount)).scalar() or 0
        
        # Get paid vs outstanding
        paid_invoices = db.query(func.count(Invoice.id)).filter(Invoice.status == "paid").scalar()
        outstanding_invoices = db.query(func.count(Invoice.id)).filter(Invoice.status == "pending").scalar()
        
        # Get total payments
        total_payments = db.query(func.count(Payment.id)).scalar()
        total_payment_amount = db.query(func.sum(Payment.amount)).scalar() or 0
        
        return {
            "total_patients": total_patients,
            "total_invoices": total_invoices,
            "total_invoice_amount": float(total_invoice_amount),
            "paid_invoices": paid_invoices,
            "outstanding_invoices": outstanding_invoices,
            "total_payments": total_payments,
            "total_payment_amount": float(total_payment_amount),
            "outstanding_amount": float(total_invoice_amount - total_payment_amount)
        }
    finally:
        db.close()

# Tool to get recent activity
def get_recent_activity(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent invoices and payments activity."""
    db = next(get_db())
    try:
        # Get recent invoices
        recent_invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).limit(limit).all()
        
        # Get recent payments
        recent_payments = db.query(Payment).order_by(Payment.created_at.desc()).limit(limit).all()
        
        # Combine and sort by date
        activities = []
        
        for invoice in recent_invoices:
            activities.append({
                "type": "invoice",
                "id": invoice.id,
                "patient_id": invoice.patient_id,
                "amount": float(invoice.amount),
                "status": invoice.status,
                "created_at": invoice.created_at.isoformat() if invoice.created_at else None
            })
        
        for payment in recent_payments:
            activities.append({
                "type": "payment",
                "id": payment.id,
                "patient_id": payment.patient_id,
                "amount": float(payment.amount),
                "status": payment.status,
                "created_at": payment.created_at.isoformat() if payment.created_at else None
            })
        
        # Sort by created_at descending
        activities.sort(key=lambda x: x["created_at"], reverse=True)
        return activities[:limit]
    finally:
        db.close()

# Tool to set theme color (for UI customization)
def set_theme_color(color: str) -> Dict[str, str]:
    """Set the theme color for the clinic billing system UI."""
    return {
        "message": f"Theme color set to {color}",
        "color": color
    }

# Tool to get invoice by invoice number
def get_invoice_by_number(invoice_number: str) -> Dict[str, Any]:
    """Get invoice information by invoice number (e.g., CLINIC-202510-0038)."""
    db = next(get_db())
    try:
        invoice = db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()
        if not invoice:
            return {"error": f"Invoice with number {invoice_number} not found"}
        
        # Get related patient information
        patient = db.query(Patient).filter(Patient.id == invoice.patient_id).first()
        
        # Get invoice items
        items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice.id).all()
        
        # Get related payments
        payments = db.query(Payment).filter(Payment.invoice_id == invoice.id).all()
        
        return {
            "invoice": {
                "id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
                "patient_id": str(invoice.patient_id),
                "patient_name": patient.name if patient else "Unknown",
                "patient_email": patient.email if patient else "Unknown",
                "total_amount": float(invoice.total_amount_cents / 100),  # Convert cents to dollars
                "currency": invoice.currency,
                "status": invoice.status,
                "payment_method": invoice.payment_method,
                "issued_at": invoice.issued_at.isoformat() if invoice.issued_at else None,
                "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                "created_at": invoice.created_at.isoformat() if invoice.created_at else None
            },
            "items": [
                {
                    "id": str(item.id),
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price_cents / 100),
                    "tax": float(item.tax_cents / 100),
                    "total": float((item.unit_price_cents * item.quantity + item.tax_cents) / 100)
                } for item in items
            ],
            "payments": [
                {
                    "id": str(payment.id),
                    "amount": float(payment.amount_cents / 100),
                    "status": payment.status,
                    "payment_method": payment.payment_method,
                    "received_at": payment.received_at.isoformat() if payment.received_at else None
                } for payment in payments
            ]
        }
    finally:
        db.close()

# Tool to get weather (example from the tutorial)
def get_weather(location: str) -> Dict[str, Any]:
    """Get weather information for a given location."""
    # This is a mock implementation - in a real scenario, you'd call a weather API
    return {
        "location": location,
        "temperature": "72°F",
        "condition": "Sunny",
        "humidity": "45%",
        "message": f"Weather in {location}: 72°F and sunny with 45% humidity"
    }

# Create the clinic billing agent
clinic_agent = LlmAgent(
    name="ClinicBillingAgent",
    model="gemini-2.5-flash",
    instruction="""
    You are an AI assistant for a clinic billing system. You help staff and patients with:

    1. **Patient Management**: Search for patients, view patient details, and manage patient information
    2. **Billing Operations**: View invoices, payments, and billing summaries
    3. **Invoice Lookup**: Find invoices by invoice number (e.g., CLINIC-202510-0038)
    4. **System Analytics**: Provide insights on revenue, outstanding amounts, and recent activity
    5. **UI Customization**: Help customize the interface theme and appearance

    IMPORTANT RULES:
    1. Always use the appropriate tools when users ask for specific information
    2. For patient searches, use search_patients with the query term
    3. For detailed patient info, use get_patient_info with the patient ID
    4. For invoice lookup by number, use get_invoice_by_number with the invoice number
    5. For billing overview, use get_billing_summary
    6. For recent activity, use get_recent_activity
    7. Be helpful and provide clear, actionable information
    8. If you don't have access to certain data, explain what information is available

    Examples of when to use tools:
    - "Find patient John Smith" → Use search_patients with "John Smith"
    - "Show me patient details for ID 123" → Use get_patient_info with 123
    - "Find invoice CLINIC-202510-0038" → Use get_invoice_by_number with "CLINIC-202510-0038"
    - "What's our billing summary?" → Use get_billing_summary
    - "Show recent activity" → Use get_recent_activity
    - "Set theme to blue" → Use set_theme_color with "blue"
    - "What's the weather in New York?" → Use get_weather with "New York"

    Always provide helpful context and explanations with your responses.
    """,
    tools=[
        FunctionTool(
            name="get_patient_info",
            description="Get detailed information about a patient by ID",
            parameters=[
                FunctionDeclaration.Parameter(
                    name="patient_id",
                    type=types.Type.INTEGER,
                    description="The ID of the patient to retrieve information for"
                )
            ],
            func=get_patient_info
        ),
        FunctionTool(
            name="search_patients",
            description="Search for patients by name or email",
            parameters=[
                FunctionDeclaration.Parameter(
                    name="query",
                    type=types.Type.STRING,
                    description="Search term to find patients by name or email"
                )
            ],
            func=search_patients
        ),
        FunctionTool(
            name="get_billing_summary",
            description="Get overall billing summary including revenue and outstanding amounts",
            parameters=[],
            func=get_billing_summary
        ),
        FunctionTool(
            name="get_recent_activity",
            description="Get recent invoices and payments activity",
            parameters=[
                FunctionDeclaration.Parameter(
                    name="limit",
                    type=types.Type.INTEGER,
                    description="Maximum number of activities to return (default: 10)"
                )
            ],
            func=get_recent_activity
        ),
        FunctionTool(
            name="set_theme_color",
            description="Set the theme color for the clinic billing system UI",
            parameters=[
                FunctionDeclaration.Parameter(
                    name="color",
                    type=types.Type.STRING,
                    description="Color name or hex code for the theme"
                )
            ],
            func=set_theme_color
        ),
        FunctionTool(
            name="get_invoice_by_number",
            description="Get invoice information by invoice number (e.g., CLINIC-202510-0038)",
            parameters=[
                FunctionDeclaration.Parameter(
                    name="invoice_number",
                    type=types.Type.STRING,
                    description="The invoice number to search for (e.g., CLINIC-202510-0038)"
                )
            ],
            func=get_invoice_by_number
        ),
        FunctionTool(
            name="get_weather",
            description="Get weather information for a given location",
            parameters=[
                FunctionDeclaration.Parameter(
                    name="location",
                    type=types.Type.STRING,
                    description="Location to get weather for"
                )
            ],
            func=get_weather
        )
    ]
)

# Create session service and runner
session_service = InMemorySessionService()
runner = Runner(agent=clinic_agent, session_service=session_service)

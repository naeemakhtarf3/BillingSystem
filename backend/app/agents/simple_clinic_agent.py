# Simplified clinic agent that works with your existing FastAPI setup
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import your existing models and services
from app.models.patient import Patient
from app.models.invoice import Invoice
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
                    "amount": float(invoice.total_amount_cents / 100),  # Convert cents to dollars
                    "status": invoice.status,
                    "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                    "created_at": invoice.created_at.isoformat() if invoice.created_at else None
                } for invoice in invoices
            ],
            "payments": [
                {
                    "id": payment.id,
                    "amount": float(payment.amount_cents / 100),  # Convert cents to dollars
                    "status": payment.status,
                    "created_at": payment.received_at.isoformat() if payment.received_at else None
                } for payment in payments
            ]
        }
    finally:
        db.close()

# Tool to search patients by name or email
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
        total_invoice_amount_cents = db.query(func.sum(Invoice.total_amount_cents)).scalar() or 0
        total_invoice_amount = total_invoice_amount_cents / 100  # Convert cents to dollars
        
        # Get paid vs outstanding
        paid_invoices = db.query(func.count(Invoice.id)).filter(Invoice.status == "paid").scalar()
        outstanding_invoices = db.query(func.count(Invoice.id)).filter(Invoice.status.in_(["issued", "draft"])).scalar()
        
        # Get total payments
        total_payments = db.query(func.count(Payment.id)).scalar()
        total_payment_amount_cents = db.query(func.sum(Payment.amount_cents)).scalar() or 0
        total_payment_amount = total_payment_amount_cents / 100  # Convert cents to dollars
        
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
        recent_payments = db.query(Payment).order_by(Payment.received_at.desc()).limit(limit).all()
        
        # Combine and sort by date
        activities = []
        
        for invoice in recent_invoices:
            activities.append({
                "type": "invoice",
                "id": invoice.id,
                "patient_id": invoice.patient_id,
                "amount": float(invoice.total_amount_cents / 100),  # Convert cents to dollars
                "status": invoice.status,
                "created_at": invoice.created_at.isoformat() if invoice.created_at else None
            })
        
        for payment in recent_payments:
            activities.append({
                "type": "payment",
                "id": payment.id,
                "invoice_id": payment.invoice_id,
                "amount": float(payment.amount_cents / 100),  # Convert cents to dollars
                "status": payment.status,
                "created_at": payment.received_at.isoformat() if payment.received_at else None
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
        from app.models.invoice import InvoiceItem
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

# Create a simple FastAPI app for the agent endpoints
agent_app = FastAPI(title="Clinic Billing Agent API")

# Add CORS middleware
agent_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Pydantic models for request/response
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union
from fastapi import Request

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    stream: bool = False

class ChatResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None

@agent_app.get("/")
async def agent_root():
    return {"message": "Clinic Billing Agent API", "status": "active"}

@agent_app.options("/chat")
async def chat_options():
    """Handle CORS preflight requests."""
    return {"message": "OK"}

# Main chat endpoint that CopilotKit expects
@agent_app.post("/chat")
async def chat_with_agent(request: Request):
    """Main chat endpoint for CopilotKit integration."""
    try:
        # Get raw request body
        body = await request.json()
        print(f"Raw request body: {body}")
        
        # Try to parse the request flexibly
        messages = []
        if "messages" in body:
            messages = body["messages"]
        elif "message" in body:
            # Handle single message format
            messages = [{"role": "user", "content": body["message"]}]
        elif "content" in body:
            # Handle direct content format
            messages = [{"role": "user", "content": body["content"]}]
        else:
            # Try to extract from any text field
            for key, value in body.items():
                if isinstance(value, str) and len(value) > 0:
                    messages = [{"role": "user", "content": value}]
                    break
        
        print(f"Parsed messages: {messages}")
        
        # Get the last message from the user
        if not messages:
            return {"message": "Hello! I'm your Clinic Billing Assistant. How can I help you today?"}
        
        last_message = messages[-1]
        user_input = last_message.get("content", "").lower()
        
        # Simple command processing
        if "find patient" in user_input or "search patient" in user_input:
            # Extract patient name from the message
            parts = user_input.split()
            if len(parts) > 2:
                patient_name = " ".join(parts[2:])  # Everything after "find patient"
                patients = search_patients(patient_name)
                if patients:
                    response = f"Found {len(patients)} patient(s) matching '{patient_name}':\n"
                    for patient in patients:
                        response += f"- ID: {patient['id']}, Name: {patient['name']}, Email: {patient['email']}\n"
                else:
                    response = f"No patients found matching '{patient_name}'"
            else:
                response = "Please provide a patient name to search for. Example: 'Find patient John Smith'"
            
            return {"message": response, "data": {"patients": patients if 'patients' in locals() else []}}
        
        elif "billing summary" in user_input or "show me the billing" in user_input:
            summary = get_billing_summary()
            response = f"""Billing Summary:
- Total Patients: {summary['total_patients']}
- Total Invoices: {summary['total_invoices']}
- Total Invoice Amount: ${summary['total_invoice_amount']:.2f}
- Paid Invoices: {summary['paid_invoices']}
- Outstanding Invoices: {summary['outstanding_invoices']}
- Total Payments: {summary['total_payments']}
- Total Payment Amount: ${summary['total_payment_amount']:.2f}
- Outstanding Amount: ${summary['outstanding_amount']:.2f}"""
            
            return {"message": response, "data": summary}
        
        elif "recent activity" in user_input or "show recent" in user_input:
            activities = get_recent_activity(5)
            response = "Recent Activity:\n"
            for activity in activities:
                response += f"- {activity['type'].title()}: ${activity['amount']:.2f} (Status: {activity['status']})\n"
            
            return {"message": response, "data": {"activities": activities}}
        
        elif "set theme" in user_input or "change theme" in user_input:
            # Extract color from the message
            parts = user_input.split()
            if len(parts) > 2:
                color = parts[-1]  # Last word should be the color
                result = set_theme_color(color)
                response = f"Theme color has been set to {color}!"
            else:
                response = "Please specify a color. Example: 'Set the theme to blue'"
            
            return {"message": response, "data": {"theme": color if 'color' in locals() else None}}
        
        elif "invoice" in user_input and ("CLINIC-" in user_input or "clinic-" in user_input):
            # Extract invoice number from the message
            import re
            invoice_match = re.search(r'CLINIC-\d{6}-\d{4}', user_input.upper())
            if invoice_match:
                invoice_number = invoice_match.group()
                invoice_data = get_invoice_by_number(invoice_number)
                if "error" in invoice_data:
                    response = f"Sorry, {invoice_data['error']}"
                else:
                    invoice = invoice_data["invoice"]
                    response = f"""Invoice Details for {invoice_number}:
- Patient: {invoice['patient_name']} ({invoice['patient_email']})
- Amount: ${invoice['total_amount']:.2f} {invoice['currency']}
- Status: {invoice['status']}
- Created: {invoice['created_at']}
- Due Date: {invoice['due_date'] or 'Not set'}

Items:"""
                    for item in invoice_data["items"]:
                        response += f"\n  - {item['description']}: {item['quantity']} x ${item['unit_price']:.2f} = ${item['total']:.2f}"
                    
                    if invoice_data["payments"]:
                        response += "\n\nPayments:"
                        for payment in invoice_data["payments"]:
                            response += f"\n  - ${payment['amount']:.2f} ({payment['status']}) - {payment['received_at'] or 'No date'}"
                    else:
                        response += "\n\nNo payments recorded."
            else:
                response = "Please provide a valid invoice number in the format CLINIC-YYYYMM-XXXX. Example: 'Find invoice CLINIC-202510-0038'"
            
            return {"message": response, "data": invoice_data if 'invoice_data' in locals() else None}
        
        elif "weather" in user_input:
            # Extract location from the message
            parts = user_input.split()
            if "in" in parts:
                location_index = parts.index("in") + 1
                if location_index < len(parts):
                    location = " ".join(parts[location_index:])
                    weather = get_weather(location)
                    response = f"Weather in {location}: {weather['temperature']}, {weather['condition']}, Humidity: {weather['humidity']}"
                else:
                    response = "Please specify a location. Example: 'Get weather in New York'"
            else:
                response = "Please specify a location. Example: 'Get weather in New York'"
            
            return {"message": response, "data": weather if 'weather' in locals() else None}
        
        else:
            # Default response for unrecognized commands
            response = """I'm your Clinic Billing Assistant! I can help you with:

**Patient Management:**
- "Find patient [name]" - Search for patients
- "Show patient details for ID [number]" - Get patient information

**Billing Operations:**
- "Show me the billing summary" - View revenue and outstanding amounts
- "Show recent activity" - See recent invoices and payments
- "Find invoice CLINIC-202510-0038" - Search for invoices by invoice number

**UI Customization:**
- "Set the theme to [color]" - Change the interface color

**Other:**
- "Get weather in [location]" - Check weather information

What would you like me to help you with?"""
            
            return {"message": response}
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return {"message": f"Sorry, I encountered an error: {str(e)}"}

# Alternative endpoint that accepts any JSON
@agent_app.post("/chat/any")
async def chat_any_format(request: Request):
    """Flexible chat endpoint that accepts any JSON format."""
    try:
        body = await request.json()
        print(f"Any format request: {body}")
        
        # Extract text from any field
        text = ""
        for key, value in body.items():
            if isinstance(value, str) and len(value.strip()) > 0:
                text = value.strip()
                break
            elif isinstance(value, list) and len(value) > 0:
                # Look for content in list items
                for item in value:
                    if isinstance(item, dict) and "content" in item:
                        text = item["content"]
                        break
                    elif isinstance(item, str):
                        text = item
                        break
        
        if not text:
            return {"message": "Hello! I'm your Clinic Billing Assistant. How can I help you today?"}
        
        user_input = text.lower()
        
        # Process the same way as the main chat endpoint
        if "invoice" in user_input and ("CLINIC-" in user_input or "clinic-" in user_input):
            # Extract invoice number from the message
            import re
            invoice_match = re.search(r'CLINIC-\d{6}-\d{4}', user_input.upper())
            if invoice_match:
                invoice_number = invoice_match.group()
                invoice_data = get_invoice_by_number(invoice_number)
                if "error" in invoice_data:
                    response_content = f"Sorry, {invoice_data['error']}"
                else:
                    invoice = invoice_data["invoice"]
                    response_content = f"""Invoice Details for {invoice_number}:
- Patient: {invoice['patient_name']} ({invoice['patient_email']})
- Amount: ${invoice['total_amount']:.2f} {invoice['currency']}
- Status: {invoice['status']}
- Created: {invoice['created_at']}
- Due Date: {invoice['due_date'] or 'Not set'}

Items:"""
                    for item in invoice_data["items"]:
                        response_content += f"\n  - {item['description']}: {item['quantity']} x ${item['unit_price']:.2f} = ${item['total']:.2f}"
                    
                    if invoice_data["payments"]:
                        response_content += "\n\nPayments:"
                        for payment in invoice_data["payments"]:
                            response_content += f"\n  - ${payment['amount']:.2f} ({payment['status']}) - {payment['received_at'] or 'No date'}"
                    else:
                        response_content += "\n\nNo payments recorded."
            else:
                response_content = "Please provide a valid invoice number in the format CLINIC-YYYYMM-XXXX. Example: 'Find invoice CLINIC-202510-0038'"
            
            # Return in multiple formats to ensure compatibility
            return {
                "message": response_content,
                "data": invoice_data if 'invoice_data' in locals() else None,
                "content": response_content,
                "text": response_content,
                "response": response_content
            }
        elif "billing summary" in user_input or "show me the billing" in user_input or "billing history" in user_input:
            summary = get_billing_summary()
            response = f"""Billing Summary:
- Total Patients: {summary['total_patients']}
- Total Invoices: {summary['total_invoices']}
- Total Invoice Amount: ${summary['total_invoice_amount']:.2f}
- Paid Invoices: {summary['paid_invoices']}
- Outstanding Invoices: {summary['outstanding_invoices']}
- Total Payments: {summary['total_payments']}
- Total Payment Amount: ${summary['total_payment_amount']:.2f}
- Outstanding Amount: ${summary['outstanding_amount']:.2f}"""
            
            # Return in multiple formats to ensure compatibility
            return {
                "message": response, 
                "data": summary,
                "content": response,
                "text": response,
                "response": response
            }
        elif "find patient" in user_input or "search patient" in user_input:
            # Extract patient name from the message
            parts = user_input.split()
            if len(parts) > 2:
                patient_name = " ".join(parts[2:])  # Everything after "find patient"
                patients = search_patients(patient_name)
                if patients:
                    response = f"Found {len(patients)} patient(s) matching '{patient_name}':\n"
                    for patient in patients:
                        response += f"- ID: {patient['id']}, Name: {patient['name']}, Email: {patient['email']}\n"
                else:
                    response = f"No patients found matching '{patient_name}'"
            else:
                response = "Please provide a patient name to search for. Example: 'Find patient John Smith'"
            
            return {
                "message": response, 
                "data": {"patients": patients if 'patients' in locals() else []},
                "content": response,
                "text": response,
                "response": response
            }
        else:
            return {
                "message": f"I received your message: '{text}'. I'm your Clinic Billing Assistant! How can I help you?",
                "content": f"I received your message: '{text}'. I'm your Clinic Billing Assistant! How can I help you?",
                "text": f"I received your message: '{text}'. I'm your Clinic Billing Assistant! How can I help you?",
                "response": f"I received your message: '{text}'. I'm your Clinic Billing Assistant! How can I help you?"
            }
    
    except Exception as e:
        print(f"Error in any format endpoint: {str(e)}")
        return {"message": f"Error: {str(e)}"}

# CopilotKit GraphQL compatible endpoint
@agent_app.post("/copilot")
async def copilot_graphql_endpoint(request: Request):
    """CopilotKit GraphQL compatible endpoint."""
    try:
        body = await request.json()
        print(f"GRAPHQL - Raw request body: {body}")
        print(f"GRAPHQL - Request headers: {dict(request.headers)}")
        
        # Extract the user message from the GraphQL structure
        user_message = ""
        try:
            if "variables" in body and "data" in body["variables"]:
                data = body["variables"]["data"]
                if "messages" in data and isinstance(data["messages"], list):
                    for message in data["messages"]:
                        if isinstance(message, dict) and "textMessage" in message:
                            text_msg = message["textMessage"]
                            if text_msg.get("role") == "user":
                                user_message = text_msg.get("content", "")
                                break
        except Exception as parse_error:
            print(f"Error parsing GraphQL request: {parse_error}")
            user_message = ""
        
        print(f"GRAPHQL - Extracted user message: {user_message}")
        
        if not user_message:
            response_content = "Hello! I'm your Clinic Billing Assistant. How can I help you today?"
        else:
            user_input = user_message.lower()
            
            # Process the request
            if "invoice" in user_input and ("CLINIC-" in user_input or "clinic-" in user_input):
                # Extract invoice number from the message
                import re
                invoice_match = re.search(r'CLINIC-\d{6}-\d{4}', user_input.upper())
                if invoice_match:
                    invoice_number = invoice_match.group()
                    invoice_data = get_invoice_by_number(invoice_number)
                    if "error" in invoice_data:
                        response_content = f"Sorry, {invoice_data['error']}"
                    else:
                        invoice = invoice_data["invoice"]
                        response_content = f"""Invoice Details for {invoice_number}:
- Patient: {invoice['patient_name']} ({invoice['patient_email']})
- Amount: ${invoice['total_amount']:.2f} {invoice['currency']}
- Status: {invoice['status']}
- Created: {invoice['created_at']}
- Due Date: {invoice['due_date'] or 'Not set'}

Items:"""
                        for item in invoice_data["items"]:
                            response_content += f"\n  - {item['description']}: {item['quantity']} x ${item['unit_price']:.2f} = ${item['total']:.2f}"
                        
                        if invoice_data["payments"]:
                            response_content += "\n\nPayments:"
                            for payment in invoice_data["payments"]:
                                response_content += f"\n  - ${payment['amount']:.2f} ({payment['status']}) - {payment['received_at'] or 'No date'}"
                        else:
                            response_content += "\n\nNo payments recorded."
                else:
                    response_content = "Please provide a valid invoice number in the format CLINIC-YYYYMM-XXXX. Example: 'Find invoice CLINIC-202510-0038'"
            elif "billing summary" in user_input or "show me the billing" in user_input or "billing history" in user_input:
                summary = get_billing_summary()
                response_content = f"""Billing Summary:
- Total Patients: {summary['total_patients']}
- Total Invoices: {summary['total_invoices']}
- Total Invoice Amount: ${summary['total_invoice_amount']:.2f}
- Paid Invoices: {summary['paid_invoices']}
- Outstanding Invoices: {summary['outstanding_invoices']}
- Total Payments: {summary['total_payments']}
- Total Payment Amount: ${summary['total_payment_amount']:.2f}
- Outstanding Amount: ${summary['outstanding_amount']:.2f}"""
            elif "find patient" in user_input or "search patient" in user_input:
                # Extract patient name from the message
                parts = user_input.split()
                if len(parts) > 2:
                    patient_name = " ".join(parts[2:])  # Everything after "find patient"
                    patients = search_patients(patient_name)
                    if patients:
                        response_content = f"Found {len(patients)} patient(s) matching '{patient_name}':\n"
                        for patient in patients:
                            response_content += f"- ID: {patient['id']}, Name: {patient['name']}, Email: {patient['email']}\n"
                    else:
                        response_content = f"No patients found matching '{patient_name}'"
                else:
                    response_content = "Please provide a patient name to search for. Example: 'Find patient John Smith'"
            else:
                response_content = f"I received your message: '{user_message}'. I'm your Clinic Billing Assistant! How can I help you?"
        
        # Return in CopilotKit GraphQL format
        return {
            "data": {
                "generateCopilotResponse": {
                    "threadId": "708bdca2-46e6-4e42-aba5-2d3e1a669602",
                    "runId": "run-123",
                    "extensions": {
                        "openaiAssistantAPI": {
                            "runId": "run-123",
                            "threadId": "708bdca2-46e6-4e42-aba5-2d3e1a669602",
                            "__typename": "OpenAIAssistantAPIExtension"
                        },
                        "__typename": "CopilotExtensions"
                    },
                    "status": {
                        "code": "SUCCESS",
                        "__typename": "SuccessResponseStatus"
                    },
                    "messages": [
                        {
                            "id": "msg-123",
                            "createdAt": "2025-10-10T15:34:45.321Z",
                            "status": {
                                "code": "SUCCESS",
                                "__typename": "SuccessMessageStatus"
                            },
                            "content": response_content,
                            "role": "assistant",
                            "parentMessageId": None,
                            "__typename": "TextMessageOutput"
                        }
                    ],
                    "metaEvents": [],
                    "__typename": "CopilotResponse"
                }
            }
        }
        
    except Exception as e:
        print(f"GRAPHQL - Error: {str(e)}")
        return {
            "data": {
                "generateCopilotResponse": {
                    "threadId": "708bdca2-46e6-4e42-aba5-2d3e1a669602",
                    "runId": "run-123",
                    "extensions": {
                        "openaiAssistantAPI": {
                            "runId": "run-123",
                            "threadId": "708bdca2-46e6-4e42-aba5-2d3e1a669602",
                            "__typename": "OpenAIAssistantAPIExtension"
                        },
                        "__typename": "CopilotExtensions"
                    },
                    "status": {
                        "code": "FAILED",
                        "reason": "Internal server error",
                        "details": str(e),
                        "__typename": "FailedResponseStatus"
                    },
                    "messages": [
                        {
                            "id": "msg-error",
                            "createdAt": "2025-10-10T15:34:45.321Z",
                            "status": {
                                "code": "FAILED",
                                "reason": str(e),
                                "__typename": "FailedMessageStatus"
                            },
                            "content": f"Sorry, I encountered an error: {str(e)}",
                            "role": "assistant",
                            "parentMessageId": None,
                            "__typename": "TextMessageOutput"
                        }
                    ],
                    "metaEvents": [],
                    "__typename": "CopilotResponse"
                }
            }
        }

@agent_app.get("/patient/{patient_id}")
async def get_patient_endpoint(patient_id: int):
    """Get patient information by ID."""
    return get_patient_info(patient_id)

@agent_app.get("/patients/search")
async def search_patients_endpoint(query: str):
    """Search for patients by name or email."""
    return search_patients(query)

@agent_app.get("/billing/summary")
async def get_billing_summary_endpoint():
    """Get billing summary."""
    return get_billing_summary()

@agent_app.get("/activity/recent")
async def get_recent_activity_endpoint(limit: int = 10):
    """Get recent activity."""
    return get_recent_activity(limit)

@agent_app.post("/theme/set")
async def set_theme_endpoint(color: str):
    """Set theme color."""
    return set_theme_color(color)

@agent_app.get("/invoice/{invoice_number}")
async def get_invoice_endpoint(invoice_number: str):
    """Get invoice information by invoice number."""
    return get_invoice_by_number(invoice_number)

@agent_app.get("/weather/{location}")
async def get_weather_endpoint(location: str):
    """Get weather information."""
    return get_weather(location)

# Health check endpoint
@agent_app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "clinic_billing_agent"}

# Additional endpoint that CopilotKit might expect
@agent_app.post("/")
async def agent_post_root():
    """Root POST endpoint for CopilotKit."""
    return {"message": "Clinic Billing Agent API", "status": "active", "endpoints": ["/chat", "/health"]}

# Streaming endpoint for CopilotKit
@agent_app.post("/stream")
async def stream_chat(request: ChatRequest):
    """Streaming chat endpoint for CopilotKit."""
    try:
        if not request.messages:
            return {"message": "Hello! I'm your Clinic Billing Assistant. How can I help you today?"}
        
        last_message = request.messages[-1]
        user_input = last_message.content.lower()
        
        # For now, return the same response as the regular chat endpoint
        # In a real implementation, this would stream the response
        if "billing summary" in user_input or "show me the billing" in user_input:
            summary = get_billing_summary()
            response = f"""Billing Summary:
- Total Patients: {summary['total_patients']}
- Total Invoices: {summary['total_invoices']}
- Total Invoice Amount: ${summary['total_invoice_amount']:.2f}
- Paid Invoices: {summary['paid_invoices']}
- Outstanding Invoices: {summary['outstanding_invoices']}
- Total Payments: {summary['total_payments']}
- Total Payment Amount: ${summary['total_payment_amount']:.2f}
- Outstanding Amount: ${summary['outstanding_amount']:.2f}"""
            
            return {"message": response, "data": summary}
        else:
            return {"message": "I'm your Clinic Billing Assistant! How can I help you?"}
    
    except Exception as e:
        return {"message": f"Sorry, I encountered an error: {str(e)}"}

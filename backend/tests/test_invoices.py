import pytest
from fastapi.testclient import TestClient
from app.models.staff import Staff, StaffRole
from app.models.patient import Patient
from app.core.security import get_password_hash

def create_test_staff(test_db):
    """Helper function to create test staff."""
    staff = Staff(
        email="test@clinic.com",
        password_hash=get_password_hash("testpassword"),
        name="Test Staff",
        role=StaffRole.BILLING_CLERK
    )
    test_db.add(staff)
    test_db.commit()
    test_db.refresh(staff)
    return staff

def create_test_patient(test_db):
    """Helper function to create test patient."""
    patient = Patient(
        name="John Doe",
        email="john.doe@email.com",
        phone="+1-555-0123"
    )
    test_db.add(patient)
    test_db.commit()
    test_db.refresh(patient)
    return patient

def get_auth_token(client, test_db):
    """Helper function to get authentication token."""
    create_test_staff(test_db)
    
    response = client.post("/api/v1/auth/login", data={
        "username": "test@clinic.com",
        "password": "testpassword"
    })
    
    return response.json()["access_token"]

def test_create_invoice(client, test_db):
    """Test invoice creation."""
    token = get_auth_token(client, test_db)
    patient = create_test_patient(test_db)
    
    invoice_data = {
        "patient_id": str(patient.id),
        "currency": "USD",
        "due_date": "2024-12-31",
        "items": [
            {
                "description": "Consultation",
                "quantity": 1,
                "unit_price_cents": 15000,
                "tax_cents": 1200
            },
            {
                "description": "Blood Test",
                "quantity": 1,
                "unit_price_cents": 8500,
                "tax_cents": 680
            }
        ]
    }
    
    response = client.post(
        "/api/v1/invoices",
        json=invoice_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["patient_id"] == str(patient.id)
    assert data["currency"] == "USD"
    assert data["total_amount_cents"] == 25380  # 15000 + 1200 + 8500 + 680
    assert data["status"] == "draft"
    assert len(data["items"]) == 2
    assert data["invoice_number"].startswith("CLINIC-")

def test_create_invoice_invalid_patient(client, test_db):
    """Test invoice creation with invalid patient ID."""
    token = get_auth_token(client, test_db)
    
    invoice_data = {
        "patient_id": "123e4567-e89b-12d3-a456-426614174000",
        "currency": "USD",
        "items": [
            {
                "description": "Consultation",
                "quantity": 1,
                "unit_price_cents": 15000,
                "tax_cents": 1200
            }
        ]
    }
    
    response = client.post(
        "/api/v1/invoices",
        json=invoice_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404
    assert "Patient not found" in response.json()["detail"]

def test_get_invoice(client, test_db):
    """Test getting a specific invoice."""
    token = get_auth_token(client, test_db)
    patient = create_test_patient(test_db)
    
    # Create invoice first
    invoice_data = {
        "patient_id": str(patient.id),
        "currency": "USD",
        "items": [
            {
                "description": "Consultation",
                "quantity": 1,
                "unit_price_cents": 15000,
                "tax_cents": 1200
            }
        ]
    }
    
    create_response = client.post(
        "/api/v1/invoices",
        json=invoice_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    invoice_id = create_response.json()["id"]
    
    # Get invoice
    response = client.get(
        f"/api/v1/invoices/{invoice_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == invoice_id
    assert data["patient_id"] == str(patient.id)
    assert len(data["items"]) == 1

def test_list_invoices(client, test_db):
    """Test listing invoices with filters."""
    token = get_auth_token(client, test_db)
    patient = create_test_patient(test_db)
    
    # Create invoice
    invoice_data = {
        "patient_id": str(patient.id),
        "currency": "USD",
        "items": [
            {
                "description": "Consultation",
                "quantity": 1,
                "unit_price_cents": 15000,
                "tax_cents": 1200
            }
        ]
    }
    
    client.post(
        "/api/v1/invoices",
        json=invoice_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # List invoices
    response = client.get(
        "/api/v1/invoices",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["patient_id"] == str(patient.id)

def test_issue_invoice(client, test_db):
    """Test issuing an invoice."""
    token = get_auth_token(client, test_db)
    patient = create_test_patient(test_db)
    
    # Create draft invoice
    invoice_data = {
        "patient_id": str(patient.id),
        "currency": "USD",
        "items": [
            {
                "description": "Consultation",
                "quantity": 1,
                "unit_price_cents": 15000,
                "tax_cents": 1200
            }
        ]
    }
    
    create_response = client.post(
        "/api/v1/invoices",
        json=invoice_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    invoice_id = create_response.json()["id"]
    
    # Issue invoice
    response = client.post(
        f"/api/v1/invoices/{invoice_id}/issue",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "issued"
    assert data["issued_at"] is not None

def test_cancel_invoice(client, test_db):
    """Test cancelling an invoice."""
    token = get_auth_token(client, test_db)
    patient = create_test_patient(test_db)
    
    # Create draft invoice
    invoice_data = {
        "patient_id": str(patient.id),
        "currency": "USD",
        "items": [
            {
                "description": "Consultation",
                "quantity": 1,
                "unit_price_cents": 15000,
                "tax_cents": 1200
            }
        ]
    }
    
    create_response = client.post(
        "/api/v1/invoices",
        json=invoice_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    invoice_id = create_response.json()["id"]
    
    # Cancel invoice
    response = client.post(
        f"/api/v1/invoices/{invoice_id}/cancel",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"

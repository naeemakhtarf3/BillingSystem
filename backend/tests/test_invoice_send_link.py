import pytest
from app.models.staff import Staff, StaffRole
from app.models.patient import Patient
from app.core.security import get_password_hash


def create_test_staff(test_db):
    staff = Staff(
        email="test2@clinic.com",
        password_hash=get_password_hash("testpassword2"),
        name="Test Staff 2",
        role=StaffRole.BILLING_CLERK
    )
    test_db.add(staff)
    test_db.commit()
    test_db.refresh(staff)
    return staff


def create_test_patient(test_db):
    patient = Patient(
        name="Jane Doe",
        email="jane.doe@email.com",
        phone="+1-555-0199"
    )
    test_db.add(patient)
    test_db.commit()
    test_db.refresh(patient)
    return patient


def get_auth_token(client, test_db):
    create_test_staff(test_db)
    response = client.post("/api/v1/auth/login", json={"username": "test2@clinic.com", "password": "testpassword2"})
    return response.json()["access_token"]


def test_send_payment_link(client, test_db):
    token = get_auth_token(client, test_db)
    patient = create_test_patient(test_db)

    invoice_data = {
        "patient_id": str(patient.id),
        "currency": "USD",
        "payment_method": "online",
        "items": [
            {"description": "Consult", "quantity": 1, "unit_price_cents": 1000, "tax_cents": 0}
        ]
    }

    create_resp = client.post("/api/v1/invoices", json=invoice_data, headers={"Authorization": f"Bearer {token}"})
    assert create_resp.status_code == 200
    invoice_id = create_resp.json()["id"]

    # Call send-payment-link
    send_resp = client.post(f"/api/v1/payments/invoices/{invoice_id}/send-payment-link", json={"email": "naeem.akhtar@f3technologies.eu"}, headers={"Authorization": f"Bearer {token}"})
    assert send_resp.status_code == 200
    data = send_resp.json()
    assert "checkout_url" in data
    assert "sent_to" in data

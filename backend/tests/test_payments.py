import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.models.staff import Staff, StaffRole
from app.models.patient import Patient
from app.models.invoice import Invoice, InvoiceStatus
from app.core.security import get_password_hash

def create_test_staff(test_db):
    """Helper function to create test staff."""
    # Return existing staff if already created (tests may call helper multiple times)
    existing = test_db.query(Staff).filter(Staff.email == "test@clinic.com").first()
    if existing:
        return existing

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

def create_test_invoice(test_db, patient, staff, status=InvoiceStatus.DRAFT):
    """Helper function to create test invoice."""
    invoice = Invoice(
        invoice_number="CLINIC-202401-0001",
        patient_id=patient.id,
        staff_id=staff.id,
        currency="USD",
        total_amount_cents=16200,
        status=status
    )
    test_db.add(invoice)
    test_db.commit()
    test_db.refresh(invoice)
    return invoice

def get_auth_token(client, test_db):
    """Helper function to get authentication token."""
    create_test_staff(test_db)
    
    response = client.post("/api/v1/auth/login", data={
        "username": "test@clinic.com",
        "password": "testpassword"
    })
    
    return response.json()["access_token"]

@patch('app.api.api_v1.endpoints.payments.stripe')
def test_create_payment_link(mock_stripe, client, test_db):
    """Test creating a Stripe payment link."""
    token = get_auth_token(client, test_db)
    staff = create_test_staff(test_db)
    patient = create_test_patient(test_db)
    invoice = create_test_invoice(test_db, patient, staff, InvoiceStatus.ISSUED)
    
    # Mock Stripe response
    mock_session = MagicMock()
    mock_session.id = "cs_test_123"
    mock_session.url = "https://checkout.stripe.com/test"
    mock_stripe.checkout.Session.create.return_value = mock_session
    
    response = client.post(
        f"/api/v1/payments/invoices/{invoice.id}/create-payment-link",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "checkout_url" in data
    assert "session_id" in data
    assert data["session_id"] == "cs_test_123"

def test_create_payment_link_draft_invoice(client, test_db):
    """Test creating payment link for draft invoice (should fail)."""
    token = get_auth_token(client, test_db)
    staff = create_test_staff(test_db)
    patient = create_test_patient(test_db)
    invoice = create_test_invoice(test_db, patient, staff, InvoiceStatus.DRAFT)
    
    response = client.post(
        f"/api/v1/payments/invoices/{invoice.id}/create-payment-link",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 400
    assert "must be issued or partially paid" in response.json()["detail"]

def test_get_invoice_payments(client, test_db):
    """Test getting payments for an invoice."""
    token = get_auth_token(client, test_db)
    staff = create_test_staff(test_db)
    patient = create_test_patient(test_db)
    invoice = create_test_invoice(test_db, patient, staff)
    
    response = client.get(
        f"/api/v1/payments/invoices/{invoice.id}/payments",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@patch('app.api.api_v1.endpoints.payments.stripe')
def test_refund_payment(mock_stripe, client, test_db):
    """Test processing a payment refund."""
    # Create admin staff for refund
    admin_staff = Staff(
        email="admin@clinic.com",
        password_hash=get_password_hash("adminpassword"),
        name="Admin Staff",
        role=StaffRole.ADMIN
    )
    test_db.add(admin_staff)
    test_db.commit()
    test_db.refresh(admin_staff)
    
    # Login as admin
    response = client.post("/api/v1/auth/login", data={
        "username": "admin@clinic.com",
        "password": "adminpassword"
    })
    token = response.json()["access_token"]
    
    # Create test data
    patient = create_test_patient(test_db)
    invoice = create_test_invoice(test_db, patient, admin_staff)
    
    # Mock Stripe refund response
    mock_refund = MagicMock()
    mock_refund.id = "re_test_123"
    mock_refund.amount = 16200
    mock_stripe.Refund.create.return_value = mock_refund
    
    # Create a mock payment
    from app.models.payment import Payment, PaymentStatus
    payment = Payment(
        invoice_id=invoice.id,
        stripe_payment_id="pi_test_123",
        amount_cents=16200,
        currency="USD",
        status=PaymentStatus.SUCCEEDED
    )
    test_db.add(payment)
    test_db.commit()
    test_db.refresh(payment)
    
    response = client.post(
        f"/api/v1/payments/{payment.id}/refund",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["refund_id"] == "re_test_123"
    assert data["status"] == "refunded"

def test_refund_payment_insufficient_permissions(client, test_db):
    """Test refund with insufficient permissions."""
    token = get_auth_token(client, test_db)  # Billing clerk token
    staff = create_test_staff(test_db)
    patient = create_test_patient(test_db)
    invoice = create_test_invoice(test_db, patient, staff)
    
    # Create a mock payment
    from app.models.payment import Payment, PaymentStatus
    payment = Payment(
        invoice_id=invoice.id,
        stripe_payment_id="pi_test_123",
        amount_cents=16200,
        currency="USD",
        status=PaymentStatus.SUCCEEDED
    )
    test_db.add(payment)
    test_db.commit()
    test_db.refresh(payment)
    
    response = client.post(
        f"/api/v1/payments/{payment.id}/refund",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]

@patch('app.api.api_v1.endpoints.payments.stripe')
def test_stripe_webhook_checkout_completed(mock_stripe, client, test_db):
    """Test Stripe webhook for completed checkout."""
    # Create test data
    staff = create_test_staff(test_db)
    patient = create_test_patient(test_db)
    invoice = create_test_invoice(test_db, patient, staff, InvoiceStatus.ISSUED)
    
    # Mock webhook event
    mock_event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "payment_intent": "pi_test_123",
                "amount_total": 16200,
                "currency": "usd",
                "metadata": {
                    "invoice_id": str(invoice.id)
                }
            }
        }
    }
    
    # Mock Stripe webhook verification
    mock_stripe.Webhook.construct_event.return_value = mock_event
    
    response = client.post(
        "/api/v1/payments/webhooks/stripe",
        json=mock_event,
        headers={"stripe-signature": "test_signature"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


@patch('app.api.api_v1.endpoints.payments.stripe')
def test_send_payment_link_and_webhook_creates_payment(mock_stripe, client, test_db):
    """End-to-end: staff sends payment link, Stripe completes checkout, webhook creates Payment and marks invoice PAID."""
    # Create test data
    staff = create_test_staff(test_db)
    patient = create_test_patient(test_db)
    invoice = create_test_invoice(test_db, patient, staff, InvoiceStatus.ISSUED)

    # Mock checkout session creation
    mock_session = MagicMock()
    mock_session.id = "cs_test_abc"
    mock_session.url = "https://checkout.stripe.com/test"
    mock_session.payment_intent = "pi_e2e_123"
    mock_session.amount_total = invoice.total_amount_cents
    mock_session.currency = invoice.currency.lower()
    mock_stripe.checkout.Session.create.return_value = mock_session

    # Login and send payment link
    token = get_auth_token(client, test_db)
    resp = client.post(f"/api/v1/payments/invoices/{invoice.id}/send-payment-link", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["session_id"] == "cs_test_abc"

    # Ensure invoice was updated with session id
    from app.db.session import get_db as _get_db
    inv = test_db.query(Invoice).filter(Invoice.id == invoice.id).first()
    assert inv.stripe_checkout_session_id == "cs_test_abc"

    # Simulate Stripe webhook for checkout.session.completed
    mock_event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_abc",
                "payment_intent": "pi_e2e_123",
                "amount_total": invoice.total_amount_cents,
                "currency": invoice.currency.lower(),
                "metadata": {
                    "invoice_id": str(invoice.id)
                }
            }
        }
    }
    mock_stripe.Webhook.construct_event.return_value = mock_event

    wh_resp = client.post("/api/v1/payments/webhooks/stripe", json=mock_event, headers={"stripe-signature": "test_sig"})
    assert wh_resp.status_code == 200
    assert wh_resp.json()["status"] == "success"

    # Verify Payment record exists and invoice marked PAID
    from app.models.payment import Payment
    payment = test_db.query(Payment).filter(Payment.stripe_payment_id == "pi_e2e_123").first()
    assert payment is not None
    inv = test_db.query(Invoice).filter(Invoice.id == invoice.id).first()
    assert inv.status == InvoiceStatus.PAID

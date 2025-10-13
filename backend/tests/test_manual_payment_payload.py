from app.models.staff import Staff, StaffRole
from app.core.security import get_password_hash
from app.models.patient import Patient
from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment
import uuid


def test_manual_payment_by_invoice_number(client, test_db):
    # create staff
    staff = Staff(email='admin@clinic.com', name='Admin')
    # set a real password hash and role so we can authenticate
    staff.password_hash = get_password_hash('adminpassword')
    staff.role = StaffRole.BILLING_CLERK
    test_db.add(staff)
    test_db.commit()
    test_db.refresh(staff)

    # create patient
    patient = Patient(name='Alice', email='alice@example.com')
    test_db.add(patient)
    test_db.commit()
    test_db.refresh(patient)

    # create invoice with invoice_number
    inv = Invoice(
        patient_id=patient.id,
        staff_id=staff.id,
        invoice_number='CLINIC-202510-0001',
        currency='USD',
        total_amount_cents=36180,
        status=InvoiceStatus.ISSUED
    )
    test_db.add(inv)
    test_db.commit()
    test_db.refresh(inv)

    payload = {
        "invoice_id": "CLINIC-202510-0001",
        "amount_cents": 36180,
        "currency": "USD",
        "method": "cash"
    }

    # Authenticate as billing clerk to obtain token
    login = client.post('/api/v1/auth/login', data={"username": "admin@clinic.com", "password": "adminpassword"})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]

    resp = client.post('/api/v1/payments', json=payload, headers={"Authorization": f"Bearer {token}"})
    print('STATUS', resp.status_code, resp.text)
    assert resp.status_code == 201, resp.text

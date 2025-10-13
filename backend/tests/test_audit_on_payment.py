from app.models.staff import Staff, StaffRole
from app.models.patient import Patient
from app.models.invoice import Invoice, InvoiceStatus
from app.core.security import get_password_hash


def test_audit_created_on_manual_payment(client, test_db):
    # create admin staff
    staff = Staff(email='admin@clinic.com', name='Admin')
    staff.password_hash = get_password_hash('adminpassword')
    staff.role = StaffRole.ADMIN
    test_db.add(staff)
    test_db.commit()
    test_db.refresh(staff)

    # create patient and invoice
    patient = Patient(name='Bob', email='bob@example.com')
    test_db.add(patient)
    test_db.commit()
    test_db.refresh(patient)

    inv = Invoice(patient_id=patient.id, staff_id=staff.id, invoice_number='CLINIC-202510-9999', currency='USD', total_amount_cents=1000, status=InvoiceStatus.ISSUED)
    test_db.add(inv)
    test_db.commit()
    test_db.refresh(inv)

    # login as admin
    login = client.post('/api/v1/auth/login', data={"username": "admin@clinic.com", "password": "adminpassword"})
    assert login.status_code == 200
    token = login.json()['access_token']

    payload = {
        'invoice_id': 'CLINIC-202510-9999',
        'amount_cents': 1000,
        'currency': 'USD',
        'method': 'cash'
    }

    resp = client.post('/api/v1/payments', json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201, resp.text

    # check audit table
    import uuid
    from app.models.audit_log import AuditLog
    payment_id = resp.json()['id']
    # coerce to UUID for comparison against the UUID column in DB
    try:
        payment_uuid = uuid.UUID(payment_id)
    except Exception:
        payment_uuid = payment_id

    logs = test_db.query(AuditLog).filter(AuditLog.target_id == payment_uuid).all()
    assert len(logs) >= 1, 'Audit log not created for payment'

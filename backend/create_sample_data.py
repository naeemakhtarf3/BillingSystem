#!/usr/bin/env python3
"""
Script to create sample data for the Clinic Billing System
Run this after setting up the database and running migrations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models import *
from app.models.staff import StaffRole
from app.models.invoice import InvoiceStatus
from app.models.payment import PaymentStatus
from app.core.security import get_password_hash
from datetime import date, datetime, timedelta
import uuid

def create_sample_data():
    db = SessionLocal()
    
    try:
        # Create sample staff
        if not db.query(Staff).filter(Staff.email == "admin@clinic.com").first():
            admin_staff = Staff(
                id=uuid.uuid4(),
                email="admin@clinic.com",
                password_hash=get_password_hash("admin123"),
                name="Dr. Sarah Johnson",
                role=StaffRole.ADMIN
            )
            db.add(admin_staff)
            print("✅ Created admin staff account")
        else:
            print("Admin staff already exists")

        if not db.query(Staff).filter(Staff.email == "billing@clinic.com").first():
            billing_staff = Staff(
                id=uuid.uuid4(),
                email="billing@clinic.com",
                password_hash=get_password_hash("billing123"),
                name="Mike Chen",
                role=StaffRole.BILLING_CLERK
            )
            db.add(billing_staff)
            print("✅ Created billing staff account")
        else:
            billing_staff = db.query(Staff).filter(Staff.email == "billing@clinic.com").first()
            print("Billing staff already exists")

        db.commit()
        
        print("✅ Created sample staff accounts:")
        print(f"   Admin: admin@clinic.com / admin123")
        print(f"   Billing: billing@clinic.com / billing123")
        
        # Create sample patients
        patients_data = [
            {
                "name": "John Smith",
                "email": "john.smith@email.com",
                "phone": "+1-555-0101",
                "dob": date(1985, 3, 15),
                "metadata": {"insurance": "Blue Cross", "emergency_contact": "Jane Smith"}
            },
            {
                "name": "Emily Davis",
                "email": "emily.davis@email.com", 
                "phone": "+1-555-0102",
                "dob": date(1992, 7, 22),
                "metadata": {"insurance": "Aetna", "emergency_contact": "Robert Davis"}
            },
            {
                "name": "Michael Brown",
                "email": "michael.brown@email.com",
                "phone": "+1-555-0103", 
                "dob": date(1978, 11, 8),
                "metadata": {"insurance": "Cigna", "emergency_contact": "Lisa Brown"}
            },
            {
                "name": "Sarah Wilson",
                "email": "sarah.wilson@email.com",
                "phone": "+1-555-0104",
                "dob": date(1995, 1, 30),
                "metadata": {"insurance": "United Health", "emergency_contact": "David Wilson"}
            },
            {
                "name": "Robert Taylor",
                "email": "robert.taylor@email.com",
                "phone": "+1-555-0105",
                "dob": date(1988, 9, 12),
                "metadata": {"insurance": "Medicare", "emergency_contact": "Mary Taylor"}
            }
        ]
        
        patients = []
        for patient_data in patients_data:
            patient = Patient(**patient_data)
            db.add(patient)
            patients.append(patient)
        
        db.commit()
        print(f"✅ Created {len(patients)} sample patients")
        
        # Create sample invoices
        sample_services = [
            {"description": "General Consultation", "unit_price_cents": 15000, "tax_cents": 1200},
            {"description": "Blood Test", "unit_price_cents": 8500, "tax_cents": 680},
            {"description": "X-Ray", "unit_price_cents": 12000, "tax_cents": 960},
            {"description": "Prescription", "unit_price_cents": 4500, "tax_cents": 360},
            {"description": "Follow-up Visit", "unit_price_cents": 10000, "tax_cents": 800}
        ]
        
        # Create invoices for each patient
        for i, patient in enumerate(patients):
            # Create 1-3 invoices per patient
            num_invoices = (i % 3) + 1
            
            for j in range(num_invoices):
                # Generate invoice number
                current_date = datetime.now()
                year_month = current_date.strftime("%Y%m")
                invoice_number = f"CLINIC-{year_month}-{i*3+j+1:04d}"
                
                # Select random services
                import random
                selected_services = random.sample(sample_services, random.randint(1, 3))
                
                # Calculate total
                total_amount_cents = sum(
                    (service["unit_price_cents"] + service["tax_cents"])
                    for service in selected_services
                )
                
                # Create invoice
                invoice = Invoice(
                    invoice_number=invoice_number,
                    patient_id=patient.id,
                    staff_id=billing_staff.id,
                    currency="USD",
                    total_amount_cents=total_amount_cents,
                    status=InvoiceStatus.DRAFT if j == 0 else InvoiceStatus.ISSUED,
                    issued_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)) if j > 0 else None,
                    due_date=date.today() + timedelta(days=30)
                )
                
                db.add(invoice)
                db.flush()  # Get invoice ID
                
                # Create invoice items
                for service in selected_services:
                    item = InvoiceItem(
                        invoice_id=invoice.id,
                        description=service["description"],
                        quantity=1,
                        unit_price_cents=service["unit_price_cents"],
                        tax_cents=service["tax_cents"]
                    )
                    db.add(item)
        
        db.commit()
        print("✅ Created sample invoices with items")
        
        # Create some sample payments (for issued invoices)
        issued_invoices = db.query(Invoice).filter(Invoice.status == InvoiceStatus.ISSUED).limit(3).all()
        
        for invoice in issued_invoices:
            # Mark some invoices as paid
            if random.choice([True, False]):
                payment = Payment(
                    invoice_id=invoice.id,
                    stripe_payment_id=f"pi_test_{uuid.uuid4().hex[:24]}",
                    amount_cents=invoice.total_amount_cents,
                    currency=invoice.currency,
                    status=PaymentStatus.SUCCEEDED,
                    received_at=datetime.utcnow() - timedelta(days=random.randint(1, 10)),
                    raw_event={"type": "payment_intent.succeeded", "test": True}
                )
                db.add(payment)
                
                # Update invoice status
                invoice.status = InvoiceStatus.PAID
        
        db.commit()
        print("✅ Created sample payments")
        
        print("\n🎉 Sample data creation completed!")
        print("\nYou can now:")
        print("1. Start the backend server: uvicorn app.main:app --reload")
        print("2. Access the API docs at: http://localhost:8000/docs")
        print("3. Login with admin@clinic.com / admin123 or billing@clinic.com / billing123")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()

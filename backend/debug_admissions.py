#!/usr/bin/env python3
"""
Debug script to check admission data in the database.
"""

from app.db.session import SessionLocal
from app.models.admission import Admission, AdmissionStatus

def debug_admissions():
    db = SessionLocal()
    try:
        # Check total admissions
        total_admissions = db.query(Admission).count()
        print(f"Total admissions: {total_admissions}")
        
        # Check discharged admissions
        discharged_admissions = db.query(Admission).filter(Admission.status == AdmissionStatus.DISCHARGED).all()
        print(f"Discharged admissions: {len(discharged_admissions)}")
        
        # Check active admissions
        active_admissions = db.query(Admission).filter(Admission.status == AdmissionStatus.ACTIVE).all()
        print(f"Active admissions: {len(active_admissions)}")
        
        # Show details of first few discharged admissions
        for i, admission in enumerate(discharged_admissions[:3]):
            print(f"\nDischarged Admission {i+1}:")
            print(f"  ID: {admission.id}")
            print(f"  Patient ID: {admission.patient_id} (type: {type(admission.patient_id)})")
            print(f"  Staff ID: {admission.staff_id} (type: {type(admission.staff_id)})")
            print(f"  Room ID: {admission.room_id}")
            print(f"  Status: {admission.status}")
            print(f"  Admission Date: {admission.admission_date}")
            print(f"  Discharge Date: {admission.discharge_date}")
            
    finally:
        db.close()

if __name__ == "__main__":
    debug_admissions()

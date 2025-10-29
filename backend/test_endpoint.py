#!/usr/bin/env python3
"""
Test script to debug the active admissions endpoint
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.admission_service import AdmissionService
from app.models.admission import AdmissionStatus

def test_active_admissions():
    """Test the active admissions functionality"""
    try:
        print("Testing active admissions endpoint...")
        
        # Get database session
        db = next(get_db())
        print("✓ Database session created")
        
        # Create admission service
        admission_service = AdmissionService(db)
        print("✓ Admission service created")
        
        # Test getting admissions
        admissions = admission_service.get_admissions(
            status=AdmissionStatus.ACTIVE,
            skip=0,
            limit=100
        )
        print(f"✓ Found {len(admissions)} active admissions")
        
        # Test getting active admissions specifically
        active_admissions = admission_service.get_active_admissions(skip=0, limit=100)
        print(f"✓ Found {len(active_admissions)} active admissions via get_active_admissions")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success = test_active_admissions()
    sys.exit(0 if success else 1)

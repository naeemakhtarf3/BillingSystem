#!/usr/bin/env python3
"""
Production Database Schema Verification Script

This script verifies that the production database schema matches the expected models.
"""

import os
import sys
from pathlib import Path

def main():
    # Set environment to production
    os.environ["ENVIRONMENT"] = "production"
    
    # Add the backend directory to Python path
    backend_dir = Path(__file__).parent
    sys.path.insert(0, str(backend_dir))
    
    try:
        from app.core.config import settings
        from app.db.session import engine
        from sqlalchemy import inspect, text
        
        print(f"Environment: {settings.ENVIRONMENT}")
        print(f"Database URL: {settings.DATABASE_URL[:50]}...")
        
        # Test database connection
        print("\nTesting database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
        
        # Get database inspector
        inspector = inspect(engine)
        
        # Check if all expected tables exist
        expected_tables = [
            'staff', 'patients', 'invoices', 'invoice_items', 'payments', 
            'audit_logs', 'room', 'admission', 'etl_process_status'
        ]
        
        existing_tables = inspector.get_table_names()
        print(f"\nExisting tables: {existing_tables}")
        
        missing_tables = [table for table in expected_tables if table not in existing_tables]
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return 1
        else:
            print("✅ All expected tables exist!")
        
        # Check specific table structures
        print("\nChecking table structures...")
        
        # Check room table
        room_columns = [col['name'] for col in inspector.get_columns('room')]
        expected_room_columns = ['id', 'room_number', 'type', 'status', 'daily_rate_cents', 'created_at', 'updated_at', 'version']
        missing_room_columns = [col for col in expected_room_columns if col not in room_columns]
        if missing_room_columns:
            print(f"❌ Room table missing columns: {missing_room_columns}")
        else:
            print("✅ Room table structure is correct!")
        
        # Check admission table
        admission_columns = [col['name'] for col in inspector.get_columns('admission')]
        expected_admission_columns = ['id', 'room_id', 'patient_id', 'staff_id', 'admission_date', 'discharge_date', 'discharge_reason', 'discharge_notes', 'invoice_id', 'status', 'created_at', 'updated_at', 'version']
        missing_admission_columns = [col for col in expected_admission_columns if col not in admission_columns]
        if missing_admission_columns:
            print(f"❌ Admission table missing columns: {missing_admission_columns}")
        else:
            print("✅ Admission table structure is correct!")
        
        print("\n✅ Production database schema verification completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

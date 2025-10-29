#!/usr/bin/env python3
"""
Script to delete all records from the Admission table.
"""

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.admission import Admission

def delete_all_admissions():
    """
    Delete all records from the Admission table.
    """
    db: Session = next(get_db())
    try:
        # Count records before deletion
        count_before = db.query(Admission).count()
        print(f"Found {count_before} admission records.")

        # Delete all records
        db.query(Admission).delete()
        db.commit()

        # Count records after deletion
        count_after = db.query(Admission).count()
        print(f"Deleted {count_before - count_after} admission records. Remaining: {count_after}")

        print("✅ All admission records have been deleted successfully.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error deleting admission records: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    delete_all_admissions()

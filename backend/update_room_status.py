#!/usr/bin/env python3
"""
Update room status in database to match enum member names
"""
from app.db.session import engine
from sqlalchemy import text

def update_room_status():
    print("Updating room status to match enum member names...")
    try:
        with engine.connect() as conn:
            # Update status to match enum member names (uppercase)
            conn.execute(text("UPDATE room SET status = 'AVAILABLE' WHERE status = 'available'"))
            conn.execute(text("UPDATE room SET status = 'OCCUPIED' WHERE status = 'occupied'"))
            conn.execute(text("UPDATE room SET status = 'MAINTENANCE' WHERE status = 'maintenance'"))
            conn.commit()
            print("✓ Successfully updated room status")
            
            # Verify the update
            result = conn.execute(text('SELECT DISTINCT status FROM room'))
            print("\nRoom status in database after update:")
            for row in result.fetchall():
                print(f"  '{row[0]}'")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_room_status()

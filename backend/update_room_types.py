#!/usr/bin/env python3
"""
Update room types in database to match enum member names
"""
from app.db.session import engine
from sqlalchemy import text

def update_room_types():
    print("Updating room types to match enum member names...")
    try:
        with engine.connect() as conn:
            # Update types to match enum member names (uppercase)
            conn.execute(text("UPDATE room SET type = 'STANDARD' WHERE type = 'standard'"))
            conn.execute(text("UPDATE room SET type = 'PRIVATE' WHERE type = 'private'"))
            conn.execute(text("UPDATE room SET type = 'ICU' WHERE type = 'icu'"))
            conn.commit()
            print("✓ Successfully updated room types")
            
            # Verify the update
            result = conn.execute(text('SELECT DISTINCT type FROM room'))
            print("\nRoom types in database after update:")
            for row in result.fetchall():
                print(f"  '{row[0]}'")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_room_types()

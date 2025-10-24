#!/usr/bin/env python3
"""
Check room types in database
"""
from app.db.session import engine
from sqlalchemy import text

def check_room_types():
    print("Checking room types in database...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT DISTINCT type FROM room LIMIT 10'))
            print("Room types in database:")
            for row in result.fetchall():
                print(f"  '{row[0]}'")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_room_types()

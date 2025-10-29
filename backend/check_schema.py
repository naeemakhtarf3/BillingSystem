#!/usr/bin/env python3
"""
Check database schema for room table
"""
from app.db.session import engine
from sqlalchemy import text

def check_schema():
    print("Checking room table schema...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text('PRAGMA table_info(room)'))
            print("Room table schema:")
            for row in result.fetchall():
                print(f"  {row}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()

#!/usr/bin/env python3
"""
Check database constraints for room table
"""
from app.db.session import engine
from sqlalchemy import text

def check_constraints():
    print("Checking room table constraints...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT sql FROM sqlite_master WHERE type="table" AND name="room"'))
            print("Room table SQL:")
            for row in result.fetchall():
                print(f"  {row[0]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_constraints()

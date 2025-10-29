#!/usr/bin/env python3
import sqlite3

# Test database connection and check for rooms table
conn = sqlite3.connect('clinic_billing.db')
cursor = conn.cursor()

# Check if rooms table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='room'")
result = cursor.fetchone()

if result:
    print("Rooms table exists!")
    # Count rooms
    cursor.execute("SELECT COUNT(*) FROM room")
    count = cursor.fetchone()[0]
    print(f"Number of rooms: {count}")
    
    # Show sample rooms
    cursor.execute("SELECT room_number, type, status, daily_rate_cents FROM room LIMIT 5")
    rooms = cursor.fetchall()
    print("Sample rooms:")
    for room in rooms:
        print(f"  {room[0]} - {room[1]} - {room[2]} - ${room[3]/100}")
else:
    print("Rooms table does not exist!")

conn.close()

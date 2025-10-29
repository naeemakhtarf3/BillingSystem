#!/usr/bin/env python3
"""
Test what the live server sees for enum values
"""
import sys
sys.path.insert(0, '.')

from app.models.room import RoomType
from app.schemas.room import Room
from pydantic import ValidationError

print("Testing enum values...")
print(f"RoomType.STANDARD.value = '{RoomType.STANDARD.value}'")
print(f"RoomType.PRIVATE.value = '{RoomType.PRIVATE.value}'")
print(f"RoomType.ICU.value = '{RoomType.ICU.value}'")

print("\nTesting Pydantic validation...")
try:
    # Try to create a Room with lowercase type
    test_data = {
        "id": 1,
        "room_number": "101",
        "type": "standard",  # lowercase
        "status": "available",
        "daily_rate_cents": 10000,
        "created_at": "2025-01-01T00:00:00",
        "updated_at": "2025-01-01T00:00:00"
    }
    room = Room(**test_data)
    print(f"✓ Success! Created room with type: {room.type}")
except ValidationError as e:
    print(f"✗ Validation error: {e}")


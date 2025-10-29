#!/usr/bin/env python3
"""
Create sample room data for testing and development.

This script creates sample rooms with different types and rates
to support the patient admission and discharge workflow.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.room import Room, RoomType, RoomStatus

def create_sample_rooms():
    """Create sample room data."""
    db = SessionLocal()
    
    try:
        # Check if rooms already exist
        existing_rooms = db.query(Room).count()
        if existing_rooms > 0:
            print(f"Found {existing_rooms} existing rooms. Skipping sample data creation.")
            return
        
        # Sample room data
        sample_rooms = [
            # Standard Rooms
            {"room_number": "101", "type": RoomType.STANDARD, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 15000},  # $150/day
            {"room_number": "102", "type": RoomType.STANDARD, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 15000},
            {"room_number": "103", "type": RoomType.STANDARD, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 15000},
            {"room_number": "104", "type": RoomType.STANDARD, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 15000},
            {"room_number": "105", "type": RoomType.STANDARD, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 15000},
            {"room_number": "106", "type": RoomType.STANDARD, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 15000},
            {"room_number": "107", "type": RoomType.STANDARD, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 15000},
            {"room_number": "108", "type": RoomType.STANDARD, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 15000},
            {"room_number": "109", "type": RoomType.STANDARD, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 15000},
            {"room_number": "110", "type": RoomType.STANDARD, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 15000},
            
            # Private Rooms
            {"room_number": "201", "type": RoomType.PRIVATE, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 25000},  # $250/day
            {"room_number": "202", "type": RoomType.PRIVATE, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 25000},
            {"room_number": "203", "type": RoomType.PRIVATE, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 25000},
            {"room_number": "204", "type": RoomType.PRIVATE, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 25000},
            {"room_number": "205", "type": RoomType.PRIVATE, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 25000},
            {"room_number": "206", "type": RoomType.PRIVATE, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 25000},
            {"room_number": "207", "type": RoomType.PRIVATE, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 25000},
            {"room_number": "208", "type": RoomType.PRIVATE, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 25000},
            
            # ICU Rooms
            {"room_number": "301", "type": RoomType.ICU, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 50000},  # $500/day
            {"room_number": "302", "type": RoomType.ICU, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 50000},
            {"room_number": "303", "type": RoomType.ICU, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 50000},
            {"room_number": "304", "type": RoomType.ICU, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 50000},
            {"room_number": "305", "type": RoomType.ICU, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 50000},
            {"room_number": "306", "type": RoomType.ICU, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 50000},
            
            # Some rooms under maintenance
            {"room_number": "401", "type": RoomType.STANDARD, "status": RoomStatus.MAINTENANCE, "daily_rate_cents": 15000},
            {"room_number": "402", "type": RoomType.PRIVATE, "status": RoomStatus.MAINTENANCE, "daily_rate_cents": 25000},
        ]
        
        # Create rooms
        created_rooms = []
        for room_data in sample_rooms:
            room = Room(**room_data)
            db.add(room)
            created_rooms.append(room)
        
        # Commit the transaction
        db.commit()
        
        print(f"Successfully created {len(created_rooms)} sample rooms:")
        print(f"  - Standard rooms: {len([r for r in created_rooms if r.type == RoomType.STANDARD])}")
        print(f"  - Private rooms: {len([r for r in created_rooms if r.type == RoomType.PRIVATE])}")
        print(f"  - ICU rooms: {len([r for r in created_rooms if r.type == RoomType.ICU])}")
        print(f"  - Available: {len([r for r in created_rooms if r.status == RoomStatus.AVAILABLE])}")
        print(f"  - Under maintenance: {len([r for r in created_rooms if r.status == RoomStatus.MAINTENANCE])}")
        
    except Exception as e:
        print(f"Error creating sample rooms: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_rooms()

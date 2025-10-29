#!/usr/bin/env python3
"""
Production Database Data Population Script

This script populates the production database with initial data like rooms.
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
        from app.db.session import SessionLocal
        from app.models.room import Room, RoomType, RoomStatus
        
        print(f"Environment: {settings.ENVIRONMENT}")
        print(f"Database URL: {settings.DATABASE_URL[:50]}...")
        
        db = SessionLocal()
        
        try:
            # Check if rooms already exist
            existing_rooms = db.query(Room).count()
            if existing_rooms > 0:
                print(f"✅ {existing_rooms} rooms already exist in the database.")
                return 0
            
            # Create sample rooms
            sample_rooms = [
                # Standard rooms
                {"room_number": "101", "type": RoomType.STANDARD, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 15000},  # $150/day
                {"room_number": "102", "type": RoomType.STANDARD, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 15000},
                {"room_number": "103", "type": RoomType.STANDARD, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 15000},
                {"room_number": "104", "type": RoomType.STANDARD, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 15000},
                {"room_number": "105", "type": RoomType.STANDARD, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 15000},
                
                # Private rooms
                {"room_number": "201", "type": RoomType.PRIVATE, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 25000},  # $250/day
                {"room_number": "202", "type": RoomType.PRIVATE, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 25000},
                {"room_number": "203", "type": RoomType.PRIVATE, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 25000},
                {"room_number": "204", "type": RoomType.PRIVATE, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 25000},
                
                # ICU rooms
                {"room_number": "ICU-1", "type": RoomType.ICU, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 50000},  # $500/day
                {"room_number": "ICU-2", "type": RoomType.ICU, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 50000},
                {"room_number": "ICU-3", "type": RoomType.ICU, "status": RoomStatus.AVAILABLE, "daily_rate_cents": 50000},
                
                # Maintenance rooms
                {"room_number": "301", "type": RoomType.STANDARD, "status": RoomStatus.MAINTENANCE, "daily_rate_cents": 15000},
            ]
            
            print(f"Creating {len(sample_rooms)} rooms...")
            
            for room_data in sample_rooms:
                room = Room(**room_data)
                db.add(room)
            
            db.commit()
            print("✅ Rooms created successfully!")
            
            # Verify creation
            room_count = db.query(Room).count()
            print(f"✅ Total rooms in database: {room_count}")
            
            # Show room summary
            for room_type in RoomType:
                count = db.query(Room).filter(Room.type == room_type).count()
                print(f"  - {room_type.value}: {count} rooms")
            
        finally:
            db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

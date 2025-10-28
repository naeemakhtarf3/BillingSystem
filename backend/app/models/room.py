"""
Room model for patient admission and discharge workflow.

This module defines the Room entity representing physical rooms available
for patient admission with proper status management and concurrency control.
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.session import Base


class RoomType(str, enum.Enum):
    """Room type enumeration."""
    STANDARD = "STANDARD"
    PRIVATE = "PRIVATE"
    ICU = "ICU"


class RoomStatus(str, enum.Enum):
    """Room status enumeration."""
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    MAINTENANCE = "MAINTENANCE"


class Room(Base):
    """
    Room entity representing physical rooms available for patient admission.
    
    Attributes:
        id: Unique identifier
        room_number: Human-readable room identifier (e.g., "101A", "ICU-1")
        type: Room type (standard, private, icu)
        status: Current status (available, occupied, maintenance)
        daily_rate_cents: Daily rate in cents to avoid floating-point precision
        created_at: Record creation timestamp
        updated_at: Last modification timestamp
    """
    
    __tablename__ = "room"
    
    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(50), unique=True, nullable=False, index=True)
    type = Column(Enum(RoomType), nullable=False, index=True)
    status = Column(Enum(RoomStatus), nullable=False, default=RoomStatus.AVAILABLE, index=True)
    daily_rate_cents = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    version = Column(Integer, nullable=False, default=1)  # Optimistic locking version
    
    # Relationships
    admissions = relationship("Admission", back_populates="room", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Room(id={self.id}, room_number='{self.room_number}', type='{self.type}', status='{self.status}')>"
    
    def is_available(self) -> bool:
        """Check if room is available for admission."""
        return self.status == RoomStatus.AVAILABLE
    
    def can_be_admitted(self) -> bool:
        """Check if room can be used for admission."""
        return self.status in [RoomStatus.AVAILABLE]
    
    def can_be_updated(self) -> bool:
        """Check if room status can be updated."""
        return self.status != RoomStatus.OCCUPIED or not self.admissions or all(
            admission.status == "discharged" for admission in self.admissions
        )
    
    def get_status_history(self) -> list:
        """Get room status change history."""
        # This would query a room_status_history table
        # For now, return empty list as placeholder
        return []
    
    def add_status_change(self, new_status: RoomStatus, changed_by: int, reason: str = None) -> dict:
        """Add a status change record to history."""
        # This would insert into room_status_history table
        # For now, return placeholder data
        return {
            'room_id': self.id,
            'old_status': self.status.value,
            'new_status': new_status.value,
            'changed_by': changed_by,
            'reason': reason,
            'timestamp': self.updated_at
        }

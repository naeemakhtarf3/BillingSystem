"""
Room service for business logic operations.

This module contains the business logic for room management including
availability checking, filtering, and status management.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime

from app.models.room import Room, RoomType, RoomStatus
from app.schemas.room import RoomCreate, RoomUpdate, RoomFilter


class RoomService:
    """Service class for room business logic operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_room(self, room_data: RoomCreate) -> Room:
        """
        Create a new room.
        
        Args:
            room_data: Room creation data
            
        Returns:
            Created room instance
            
        Raises:
            ValueError: If room number already exists
        """
        # Check if room number already exists
        existing_room = self.db.query(Room).filter(Room.room_number == room_data.room_number).first()
        if existing_room:
            raise ValueError(f"Room number '{room_data.room_number}' already exists")
        
        # Create new room
        room = Room(
            room_number=room_data.room_number,
            type=room_data.type,
            daily_rate_cents=room_data.daily_rate_cents,
            status=RoomStatus.AVAILABLE
        )
        
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        
        return room
    
    def get_room(self, room_id: int) -> Optional[Room]:
        """
        Get room by ID.
        
        Args:
            room_id: Room ID
            
        Returns:
            Room instance or None if not found
        """
        return self.db.query(Room).filter(Room.id == room_id).first()
    
    def get_room_by_number(self, room_number: str) -> Optional[Room]:
        """
        Get room by room number.
        
        Args:
            room_number: Room number
            
        Returns:
            Room instance or None if not found
        """
        return self.db.query(Room).filter(Room.room_number == room_number).first()
    
    def get_rooms(self, filters: Optional[RoomFilter] = None, skip: int = 0, limit: int = 100) -> List[Room]:
        """
        Get rooms with optional filtering.
        
        Args:
            filters: Optional filtering criteria
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of room instances
        """
        query = self.db.query(Room)
        
        if filters:
            if filters.type:
                query = query.filter(Room.type == filters.type)
            if filters.status:
                query = query.filter(Room.status == filters.status)
            if filters.available_only:
                query = query.filter(Room.status == RoomStatus.AVAILABLE)
        
        return query.offset(skip).limit(limit).all()
    
    def get_rooms_with_advanced_filtering(
        self, 
        room_types: Optional[List[RoomType]] = None,
        statuses: Optional[List[RoomStatus]] = None,
        min_rate: Optional[int] = None,
        max_rate: Optional[int] = None,
        room_numbers: Optional[List[str]] = None,
        available_only: bool = False,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Room]:
        """
        Get rooms with advanced filtering options.
        
        Args:
            room_types: List of room types to filter by
            statuses: List of statuses to filter by
            min_rate: Minimum daily rate in cents
            max_rate: Maximum daily rate in cents
            room_numbers: List of room numbers to filter by
            available_only: Show only available rooms
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of room instances
        """
        query = self.db.query(Room)
        
        # Filter by room types
        if room_types:
            query = query.filter(Room.type.in_(room_types))
        
        # Filter by statuses
        if statuses:
            query = query.filter(Room.status.in_(statuses))
        elif available_only:
            query = query.filter(Room.status == RoomStatus.AVAILABLE)
        
        # Filter by rate range
        if min_rate is not None:
            query = query.filter(Room.daily_rate_cents >= min_rate)
        if max_rate is not None:
            query = query.filter(Room.daily_rate_cents <= max_rate)
        
        # Filter by room numbers
        if room_numbers:
            query = query.filter(Room.room_number.in_(room_numbers))
        
        return query.offset(skip).limit(limit).all()
    
    def get_room_statistics(self) -> dict:
        """
        Get room statistics for dashboard.
        
        Returns:
            Dictionary with room statistics
        """
        total_rooms = self.db.query(Room).count()
        available_rooms = self.db.query(Room).filter(Room.status == RoomStatus.AVAILABLE).count()
        occupied_rooms = self.db.query(Room).filter(Room.status == RoomStatus.OCCUPIED).count()
        maintenance_rooms = self.db.query(Room).filter(Room.status == RoomStatus.MAINTENANCE).count()
        
        # Room type breakdown
        type_stats = {}
        for room_type in RoomType:
            count = self.db.query(Room).filter(Room.type == room_type).count()
            type_stats[room_type.value] = count
        
        # Status breakdown
        status_stats = {}
        for status in RoomStatus:
            count = self.db.query(Room).filter(Room.status == status).count()
            status_stats[status.value] = count
        
        return {
            'total_rooms': total_rooms,
            'available_rooms': available_rooms,
            'occupied_rooms': occupied_rooms,
            'maintenance_rooms': maintenance_rooms,
            'occupancy_rate': (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0,
            'type_breakdown': type_stats,
            'status_breakdown': status_stats
        }
    
    def get_available_rooms(self, room_type: Optional[RoomType] = None) -> List[Room]:
        """
        Get available rooms for admission.
        
        Args:
            room_type: Optional room type filter
            
        Returns:
            List of available room instances
        """
        query = self.db.query(Room).filter(Room.status == RoomStatus.AVAILABLE)
        
        if room_type:
            query = query.filter(Room.type == room_type)
        
        return query.all()
    
    def update_room(self, room_id: int, room_data: RoomUpdate) -> Optional[Room]:
        """
        Update room details.
        
        Args:
            room_id: Room ID
            room_data: Room update data
            
        Returns:
            Updated room instance or None if not found
            
        Raises:
            ValueError: If room cannot be updated (e.g., has active admissions)
        """
        room = self.get_room(room_id)
        if not room:
            return None
        
        # Check if room can be updated
        if not room.can_be_updated():
            raise ValueError("Room cannot be updated while it has active admissions")
        
        # Update fields
        if room_data.status is not None:
            room.status = room_data.status
        if room_data.daily_rate_cents is not None:
            room.status = room_data.daily_rate_cents
        
        self.db.commit()
        self.db.refresh(room)
        
        return room
    
    def update_room_status(self, room_id: int, status: RoomStatus) -> Optional[Room]:
        """
        Update room status.
        
        Args:
            room_id: Room ID
            status: New room status
            
        Returns:
            Updated room instance or None if not found
            
        Raises:
            ValueError: If status transition is not allowed
        """
        room = self.get_room(room_id)
        if not room:
            return None
        
        # Validate status transition
        if not self._is_valid_status_transition(room.status, status):
            raise ValueError(f"Cannot change room status from {room.status} to {status}")
        
        room.status = status
        self.db.commit()
        self.db.refresh(room)
        
        return room
    
    def is_room_available(self, room_id: int) -> bool:
        """
        Check if room is available for admission.
        
        Args:
            room_id: Room ID
            
        Returns:
            True if room is available, False otherwise
        """
        room = self.get_room(room_id)
        return room is not None and room.is_available()
    
    def validate_room_availability(self, room_id: int) -> dict:
        """
        Comprehensive room availability validation.
        
        Args:
            room_id: Room ID
            
        Returns:
            Dictionary with availability status and details
            
        Raises:
            ValueError: If room is not available with specific reason
        """
        room = self.get_room(room_id)
        if not room:
            raise ValueError(f"Room {room_id} not found")
        
        # Check room status
        if room.status != RoomStatus.AVAILABLE:
            status_reasons = {
                RoomStatus.OCCUPIED: "Room is currently occupied",
                RoomStatus.MAINTENANCE: "Room is under maintenance"
            }
            raise ValueError(status_reasons.get(room.status, f"Room status is {room.status}"))
        
        # Check for active admissions
        from app.models.admission import Admission, AdmissionStatus
        active_admissions = self.db.query(Admission).filter(
            Admission.room_id == room_id,
            Admission.status == AdmissionStatus.ACTIVE
        ).count()
        
        if active_admissions > 0:
            raise ValueError(f"Room {room_id} has {active_admissions} active admission(s)")
        
        return {
            "available": True,
            "room_id": room_id,
            "room_number": room.room_number,
            "type": room.type,
            "daily_rate_cents": room.daily_rate_cents
        }
    
    def get_room_availability_status(self, room_id: int) -> dict:
        """
        Get detailed room availability status.
        
        Args:
            room_id: Room ID
            
        Returns:
            Dictionary with detailed availability information
        """
        room = self.get_room(room_id)
        if not room:
            return {
                "available": False,
                "reason": "Room not found",
                "room_id": room_id
            }
        
        # Check status
        if room.status != RoomStatus.AVAILABLE:
            return {
                "available": False,
                "reason": f"Room status is {room.status}",
                "room_id": room_id,
                "status": room.status
            }
        
        # Check for active admissions
        from app.models.admission import Admission, AdmissionStatus
        active_admissions = self.db.query(Admission).filter(
            Admission.room_id == room_id,
            Admission.status == AdmissionStatus.ACTIVE
        ).all()
        
        if active_admissions:
            return {
                "available": False,
                "reason": f"Room has {len(active_admissions)} active admission(s)",
                "room_id": room_id,
                "active_admissions": len(active_admissions)
            }
        
        return {
            "available": True,
            "room_id": room_id,
            "room_number": room.room_number,
            "type": room.type,
            "daily_rate_cents": room.daily_rate_cents
        }
    
    def get_room_count(self, filters: Optional[RoomFilter] = None) -> int:
        """
        Get total count of rooms matching filters.
        
        Args:
            filters: Optional filtering criteria
            
        Returns:
            Total count of rooms
        """
        query = self.db.query(Room)
        
        if filters:
            if filters.type:
                query = query.filter(Room.type == filters.type)
            if filters.status:
                query = query.filter(Room.status == filters.status)
            if filters.available_only:
                query = query.filter(Room.status == RoomStatus.AVAILABLE)
        
        return query.count()
    
    def _is_valid_status_transition(self, current_status: RoomStatus, new_status: RoomStatus) -> bool:
        """
        Validate room status transition.
        
        Args:
            current_status: Current room status
            new_status: New room status
            
        Returns:
            True if transition is valid, False otherwise
        """
        # Define valid transitions
        valid_transitions = {
            RoomStatus.AVAILABLE: [RoomStatus.OCCUPIED, RoomStatus.MAINTENANCE],
            RoomStatus.OCCUPIED: [RoomStatus.AVAILABLE],
            RoomStatus.MAINTENANCE: [RoomStatus.AVAILABLE]
        }
        
        return new_status in valid_transitions.get(current_status, [])
    
    def schedule_maintenance(self, room_id: int, maintenance_data: dict) -> dict:
        """
        Schedule room maintenance.
        
        Args:
            room_id: Room ID
            maintenance_data: Maintenance scheduling data
            
        Returns:
            Maintenance schedule details
            
        Raises:
            ValueError: If room cannot be scheduled for maintenance
        """
        room = self.get_room(room_id)
        if not room:
            raise ValueError(f"Room with ID {room_id} not found")
        
        # Validate room can be scheduled for maintenance
        if not self._can_schedule_maintenance(room):
            raise ValueError(f"Room {room.room_number} cannot be scheduled for maintenance")
        
        # Update room status to maintenance
        room.status = RoomStatus.MAINTENANCE
        
        # Store maintenance information
        maintenance_info = {
            'room_id': room_id,
            'room_number': room.room_number,
            'scheduled_date': maintenance_data.get('scheduled_date'),
            'estimated_duration': maintenance_data.get('estimated_duration'),
            'maintenance_type': maintenance_data.get('maintenance_type'),
            'description': maintenance_data.get('description'),
            'assigned_staff': maintenance_data.get('assigned_staff'),
            'priority': maintenance_data.get('priority', 'medium')
        }
        
        self.db.commit()
        self.db.refresh(room)
        
        return maintenance_info
    
    def _can_schedule_maintenance(self, room: Room) -> bool:
        """
        Check if room can be scheduled for maintenance.
        
        Args:
            room: Room instance
            
        Returns:
            True if room can be scheduled for maintenance
        """
        # Room must be available (not occupied)
        if room.status != RoomStatus.AVAILABLE:
            return False
        
        # Check for active admissions
        from app.models.admission import Admission, AdmissionStatus
        active_admissions = self.db.query(Admission).filter(
            Admission.room_id == room.id,
            Admission.status == AdmissionStatus.ACTIVE
        ).count()
        
        return active_admissions == 0
    
    def complete_maintenance(self, room_id: int, completion_data: dict) -> dict:
        """
        Complete room maintenance and return to available status.
        
        Args:
            room_id: Room ID
            completion_data: Maintenance completion data
            
        Returns:
            Completion details
            
        Raises:
            ValueError: If room is not in maintenance status
        """
        room = self.get_room(room_id)
        if not room:
            raise ValueError(f"Room with ID {room_id} not found")
        
        if room.status != RoomStatus.MAINTENANCE:
            raise ValueError(f"Room {room.room_number} is not in maintenance status")
        
        # Update room status to available
        room.status = RoomStatus.AVAILABLE
        
        # Store completion information
        completion_info = {
            'room_id': room_id,
            'room_number': room.room_number,
            'completed_date': completion_data.get('completed_date'),
            'actual_duration': completion_data.get('actual_duration'),
            'work_performed': completion_data.get('work_performed'),
            'notes': completion_data.get('notes'),
            'completed_by': completion_data.get('completed_by')
        }
        
        self.db.commit()
        self.db.refresh(room)
        
        return completion_info
    
    def get_maintenance_schedule(self) -> list:
        """
        Get rooms scheduled for maintenance.
        
        Returns:
            List of rooms in maintenance status
        """
        return self.db.query(Room).filter(Room.status == RoomStatus.MAINTENANCE).all()
    
    def get_maintenance_statistics(self) -> dict:
        """
        Get maintenance statistics.
        
        Returns:
            Dictionary with maintenance statistics
        """
        total_rooms = self.db.query(Room).count()
        maintenance_rooms = self.db.query(Room).filter(Room.status == RoomStatus.MAINTENANCE).count()
        available_rooms = self.db.query(Room).filter(Room.status == RoomStatus.AVAILABLE).count()
        occupied_rooms = self.db.query(Room).filter(Room.status == RoomStatus.OCCUPIED).count()
        
        return {
            'total_rooms': total_rooms,
            'maintenance_rooms': maintenance_rooms,
            'available_rooms': available_rooms,
            'occupied_rooms': occupied_rooms,
            'maintenance_percentage': (maintenance_rooms / total_rooms * 100) if total_rooms > 0 else 0
        }

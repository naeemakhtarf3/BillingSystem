"""
Room API endpoints for patient admission and discharge workflow.

This module provides REST endpoints for room management including
listing, filtering, and status updates.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.room import Room, RoomCreate, RoomUpdate, RoomFilter, RoomListResponse, RoomStatusUpdate
from app.services.room_service import RoomService
from app.api.api_v1.endpoints.auth import get_current_staff
from app.models.staff import Staff

router = APIRouter()


@router.get("/", response_model=RoomListResponse)
def get_rooms(
    type: Optional[str] = Query(None, description="Filter by room type"),
    status: Optional[str] = Query(None, description="Filter by room status"),
    available_only: bool = Query(False, description="Show only available rooms"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    Get rooms with optional filtering.
    
    Args:
        type: Optional room type filter
        status: Optional room status filter
        available_only: Show only available rooms
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of rooms with total count
    """
    try:
        # Create filter object
        filters = RoomFilter(
            type=type,
            status=status,
            available_only=available_only
        )
        
        # Get rooms and count
        room_service = RoomService(db)
        rooms = room_service.get_rooms(filters, skip, limit)
        total = room_service.get_room_count(filters)
        
        return RoomListResponse(
            rooms=rooms,
            total=total,
            page=skip // limit + 1,
            size=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving rooms: {str(e)}")


@router.get("/{room_id}", response_model=Room)
def get_room(room_id: int, db: Session = Depends(get_db)):
    """
    Get room by ID.
    
    Args:
        room_id: Room ID
        db: Database session
        
    Returns:
        Room details
        
    Raises:
        HTTPException: If room not found
    """
    room_service = RoomService(db)
    room = room_service.get_room(room_id)
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    return room


@router.post("/", response_model=Room, status_code=201)
def create_room(
    room_data: RoomCreate, 
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """
    Create a new room.
    
    Args:
        room_data: Room creation data
        db: Database session
        
    Returns:
        Created room details
        
    Raises:
        HTTPException: If room number already exists or validation fails
    """
    try:
        room_service = RoomService(db)
        room = room_service.create_room(room_data)
        return room
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating room: {str(e)}")


@router.put("/{room_id}", response_model=Room)
def update_room(room_id: int, room_data: RoomUpdate, db: Session = Depends(get_db)):
    """
    Update room details.
    
    Args:
        room_id: Room ID
        room_data: Room update data
        db: Database session
        
    Returns:
        Updated room details
        
    Raises:
        HTTPException: If room not found or cannot be updated
    """
    try:
        room_service = RoomService(db)
        room = room_service.update_room(room_id, room_data)
        
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        return room
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating room: {str(e)}")


@router.patch("/{room_id}/status", response_model=Room)
def update_room_status(room_id: int, status_data: RoomStatusUpdate, db: Session = Depends(get_db)):
    """
    Update room status.
    
    Args:
        room_id: Room ID
        status_data: Status update data
        db: Database session
        
    Returns:
        Updated room details
        
    Raises:
        HTTPException: If room not found or status transition not allowed
    """
    try:
        room_service = RoomService(db)
        room = room_service.update_room_status(room_id, status_data.status)
        
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        return room
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating room status: {str(e)}")


@router.get("/available/list", response_model=List[Room])
def get_available_rooms(
    type: Optional[str] = Query(None, description="Filter by room type"),
    db: Session = Depends(get_db)
):
    """
    Get available rooms for admission.
    
    Args:
        type: Optional room type filter
        db: Database session
        
    Returns:
        List of available rooms
    """
    try:
        room_service = RoomService(db)
        rooms = room_service.get_available_rooms(type)
        return rooms
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving available rooms: {str(e)}")


@router.get("/{room_id}/available")
def check_room_availability(room_id: int, db: Session = Depends(get_db)):
    """
    Check if room is available for admission.
    
    Args:
        room_id: Room ID
        db: Database session
        
    Returns:
        Availability status
        
    Raises:
        HTTPException: If room not found
    """
    try:
        room_service = RoomService(db)
        is_available = room_service.is_room_available(room_id)
        
        return {
            "room_id": room_id,
            "available": is_available
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking room availability: {str(e)}")

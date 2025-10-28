"""
Pydantic schemas for Room entity validation and serialization.

This module defines the request/response schemas for room operations
with proper validation and type safety.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

from app.models.room import RoomType, RoomStatus


class RoomBase(BaseModel):
    """Base room schema with common fields."""
    room_number: str = Field(..., min_length=1, max_length=50, description="Room number identifier")
    type: RoomType = Field(..., description="Room type")
    daily_rate_cents: int = Field(..., gt=0, description="Daily rate in cents")
    
    @validator('room_number')
    def validate_room_number(cls, v):
        """Validate room number format."""
        if not v or not v.strip():
            raise ValueError('Room number cannot be empty')
        return v.strip()


class RoomCreate(RoomBase):
    """Schema for creating a new room."""
    pass


class RoomUpdate(BaseModel):
    """Schema for updating room details."""
    status: Optional[RoomStatus] = Field(None, description="New room status")
    daily_rate_cents: Optional[int] = Field(None, gt=0, description="New daily rate in cents")
    
    @validator('daily_rate_cents')
    def validate_daily_rate(cls, v):
        """Validate daily rate is positive."""
        if v is not None and v <= 0:
            raise ValueError('Daily rate must be positive')
        return v


class RoomInDBBase(RoomBase):
    """Base schema for room in database."""
    id: int
    status: RoomStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True


class Room(RoomInDBBase):
    """Schema for room response."""
    pass


class RoomWithAdmissions(Room):
    """Schema for room response with admissions."""
    admissions: list = Field(default_factory=list, description="List of admissions for this room")


class RoomFilter(BaseModel):
    """Schema for room filtering."""
    type: Optional[RoomType] = Field(None, description="Filter by room type")
    status: Optional[RoomStatus] = Field(None, description="Filter by room status")
    available_only: Optional[bool] = Field(False, description="Show only available rooms")


class RoomListResponse(BaseModel):
    """Schema for room list response."""
    rooms: list[Room] = Field(..., description="List of rooms")
    total: int = Field(..., description="Total number of rooms")
    page: int = Field(1, description="Current page number")
    size: int = Field(10, description="Page size")


class RoomStatusUpdate(BaseModel):
    """Schema for updating room status."""
    status: RoomStatus = Field(..., description="New room status")
    
    @validator('status')
    def validate_status_transition(cls, v):
        """Validate status transition is allowed."""
        # Add business logic for status transitions if needed
        return v

"""
Admission model for patient admission and discharge workflow.

This module defines the Admission entity representing patient stays in rooms
with billing linkage and proper status management.
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.session import Base


class AdmissionStatus(str, enum.Enum):
    """Admission status enumeration."""
    ACTIVE = "active"
    DISCHARGED = "discharged"


class Admission(Base):
    """
    Admission entity representing patient stays in rooms with billing linkage.
    
    Attributes:
        id: Unique identifier
        room_id: Reference to Room
        patient_id: Reference to existing Patient
        staff_id: Reference to existing Staff (who processed admission)
        admission_date: When patient was admitted
        discharge_date: When patient was discharged (nullable)
        discharge_reason: Reason for discharge (nullable)
        discharge_notes: Additional discharge notes (nullable)
        invoice_id: Reference to generated Invoice (nullable)
        status: Current status (active, discharged)
        created_at: Record creation timestamp
        updated_at: Last modification timestamp
    """
    
    __tablename__ = "admission"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("room.id"), nullable=False, index=True)
    patient_id = Column(String, nullable=False, index=True)
    staff_id = Column(String, nullable=False, index=True)
    admission_date = Column(DateTime(timezone=True), nullable=False, index=True)
    discharge_date = Column(DateTime(timezone=True), nullable=True, index=True)
    discharge_reason = Column(String, nullable=True, index=True)
    discharge_notes = Column(Text, nullable=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True, index=True)
    status = Column(Enum(AdmissionStatus), nullable=False, default=AdmissionStatus.ACTIVE, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    version = Column(Integer, nullable=False, default=1)  # Optimistic locking version
    
    # Relationships - commented out to avoid circular import issues
    # room = relationship("Room", back_populates="admissions")
    # Note: Patient, Staff, and Invoice relationships would be defined in their respective models
    
    def __repr__(self):
        return f"<Admission(id={self.id}, room_id={self.room_id}, patient_id={self.patient_id}, status='{self.status}')>"
    
    def is_active(self) -> bool:
        """Check if admission is currently active."""
        return self.status == AdmissionStatus.ACTIVE
    
    def can_be_discharged(self) -> bool:
        """Check if admission can be discharged."""
        return self.status == AdmissionStatus.ACTIVE and self.discharge_date is None
    
    def get_duration_days(self) -> float:
        """Calculate duration of stay in days."""
        if not self.discharge_date:
            return 0.0
        
        duration = self.discharge_date - self.admission_date
        return duration.total_seconds() / (24 * 3600)  # Convert to days
    
    def get_duration_hours(self) -> float:
        """Calculate duration of stay in hours."""
        if not self.discharge_date:
            return 0.0
        
        duration = self.discharge_date - self.admission_date
        return duration.total_seconds() / 3600  # Convert to hours

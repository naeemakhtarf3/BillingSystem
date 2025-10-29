from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from app.models.room import Room
from app.models.admission import Admission, AdmissionStatus
from app.schemas.admission import BillingSummary


class BillingService:
    """Service class for billing calculations and invoice generation."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_admission_billing(self, admission: Admission) -> BillingSummary:
        """
        Calculate billing for an admission.
        
        Args:
            admission: Admission instance
            
        Returns:
            Billing summary with calculated charges
            
        Raises:
            ValueError: If admission data is invalid for billing
        """
        if not admission.discharge_date:
            raise ValueError("Cannot calculate billing without discharge date")
        
        # Get room information
        room = self.db.query(Room).filter(Room.id == admission.room_id).first()
        if not room:
            raise ValueError(f"Room with ID {admission.room_id} not found")
        
        # Calculate duration
        duration_hours = self._calculate_duration_hours(admission)
        duration_days = self._calculate_duration_days(admission)
        
        # Calculate base charges
        base_charges = self._calculate_base_charges(room, duration_hours, duration_days)
        
        # Calculate additional charges (extras, services, etc.)
        additional_charges = self._calculate_additional_charges(admission)
        
        # Calculate taxes
        taxes = self._calculate_taxes(base_charges + additional_charges)
        
        # Calculate total
        total_charges = base_charges + additional_charges + taxes
        
        return BillingSummary(
            total_charges_cents=int(total_charges),
            duration_hours=duration_hours,
            daily_rate_cents=room.daily_rate_cents,
            base_charges_cents=int(base_charges),
            additional_charges_cents=int(additional_charges),
            taxes_cents=int(taxes),
            breakdown=self._create_billing_breakdown(room, duration_hours, duration_days, base_charges, additional_charges, taxes)
        )
    
    def _calculate_duration_hours(self, admission: Admission) -> float:
        """Calculate admission duration in hours."""
        if not admission.discharge_date:
            return 0.0
        
        duration = admission.discharge_date - admission.admission_date
        return duration.total_seconds() / 3600
    
    def _calculate_duration_days(self, admission: Admission) -> float:
        """Calculate admission duration in days."""
        if not admission.discharge_date:
            return 0.0
        
        duration = admission.discharge_date - admission.admission_date
        return duration.total_seconds() / (24 * 3600)
    
    def _calculate_base_charges(self, room: Room, duration_hours: float, duration_days: float) -> int:
        """
        Calculate base room charges.
        
        Args:
            room: Room instance
            duration_hours: Duration in hours
            duration_days: Duration in days
            
        Returns:
            Base charges in cents
        """
        daily_rate_cents = room.daily_rate_cents
        
        # Same day admission/discharge (less than 24 hours)
        if duration_hours < 24:
            # Charge hourly rate for same-day stays
            hourly_rate = daily_rate_cents / 24
            return int(hourly_rate * duration_hours)
        
        # Multi-day stays
        full_days = int(duration_days)
        remaining_hours = duration_hours - (full_days * 24)
        
        # Charge full days
        base_charges = full_days * daily_rate_cents
        
        # Charge remaining hours at hourly rate
        if remaining_hours > 0:
            hourly_rate = daily_rate_cents / 24
            base_charges += int(hourly_rate * remaining_hours)
        
        return base_charges
    
    def _calculate_additional_charges(self, admission: Admission) -> int:
        """
        Calculate additional charges (services, extras, etc.).
        
        Args:
            admission: Admission instance
            
        Returns:
            Additional charges in cents
        """
        # This would integrate with existing billing system
        # For now, return 0 as placeholder
        additional_charges = 0
        
        # Example: Calculate charges based on room type
        room = self.db.query(Room).filter(Room.id == admission.room_id).first()
        if room:
            # ICU rooms might have additional monitoring charges
            if room.type == 'icu':
                duration_hours = self._calculate_duration_hours(admission)
                # $50/hour for ICU monitoring
                additional_charges += int(duration_hours * 5000)  # 5000 cents = $50
        
        return additional_charges
    
    def _calculate_taxes(self, subtotal_cents: int) -> int:
        """
        Calculate taxes on charges.
        
        Args:
            subtotal_cents: Subtotal in cents
            
        Returns:
            Tax amount in cents
        """
        # Example: 8.5% tax rate
        tax_rate = 0.085
        return int(subtotal_cents * tax_rate)
    
    def _create_billing_breakdown(self, room: Room, duration_hours: float, duration_days: float, 
                                 base_charges: int, additional_charges: int, taxes: int) -> Dict[str, Any]:
        """
        Create detailed billing breakdown.
        
        Args:
            room: Room instance
            duration_hours: Duration in hours
            duration_days: Duration in days
            base_charges: Base charges in cents
            additional_charges: Additional charges in cents
            taxes: Tax amount in cents
            
        Returns:
            Billing breakdown dictionary
        """
        return {
            'room_info': {
                'room_number': room.room_number,
                'room_type': room.type,
                'daily_rate_cents': room.daily_rate_cents,
                'daily_rate_dollars': room.daily_rate_cents / 100
            },
            'duration': {
                'hours': round(duration_hours, 2),
                'days': round(duration_days, 2),
                'formatted': self._format_duration(duration_hours)
            },
            'charges': {
                'base_charges_cents': base_charges,
                'base_charges_dollars': base_charges / 100,
                'additional_charges_cents': additional_charges,
                'additional_charges_dollars': additional_charges / 100,
                'subtotal_cents': base_charges + additional_charges,
                'subtotal_dollars': (base_charges + additional_charges) / 100
            },
            'taxes': {
                'tax_amount_cents': taxes,
                'tax_amount_dollars': taxes / 100,
                'tax_rate': 0.085
            },
            'total': {
                'total_cents': base_charges + additional_charges + taxes,
                'total_dollars': (base_charges + additional_charges + taxes) / 100
            }
        }
    
    def _format_duration(self, duration_hours: float) -> str:
        """Format duration in a human-readable format."""
        if duration_hours < 24:
            return f"{duration_hours:.1f} hours"
        
        days = int(duration_hours // 24)
        hours = duration_hours % 24
        
        if hours == 0:
            return f"{days} day{'s' if days != 1 else ''}"
        else:
            return f"{days} day{'s' if days != 1 else ''} and {hours:.1f} hours"
    
    def create_invoice(self, admission: Admission, billing_summary: BillingSummary) -> Dict[str, Any]:
        """
        Create an invoice for an admission.
        
        Args:
            admission: Admission instance
            billing_summary: Billing calculation summary
            
        Returns:
            Invoice details dictionary
        """
        # This would integrate with existing billing system
        # For now, return a placeholder invoice
        invoice_id = f"INV-{admission.id}-{int(datetime.now().timestamp())}"
        
        return {
            'id': invoice_id,
            'patient_id': admission.patient_id,
            'admission_id': admission.id,
            'room_id': admission.room_id,
            'total_amount_cents': billing_summary.total_charges_cents,
            'total_amount_dollars': billing_summary.total_charges_cents / 100,
            'status': 'pending',
            'created_at': datetime.now(),
            'due_date': datetime.now() + timedelta(days=30),
            'billing_summary': billing_summary.dict() if hasattr(billing_summary, 'dict') else billing_summary
        }
    
    def get_patient_billing_history(self, patient_id: int) -> list:
        """
        Get billing history for a patient.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            List of billing records
        """
        # This would query the billing system for patient history
        # For now, return empty list as placeholder
        return []
    
    def get_outstanding_balance(self, patient_id: int) -> int:
        """
        Get outstanding balance for a patient.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Outstanding balance in cents
        """
        # This would query the billing system for outstanding balance
        # For now, return 0 as placeholder
        return 0

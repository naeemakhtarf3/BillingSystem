"""
Admission service for business logic operations.

This module contains the business logic for admission management including
patient admission, discharge, and billing calculations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.admission import Admission, AdmissionStatus
from app.models.room import Room, RoomStatus
from app.schemas.admission import AdmissionCreate, AdmissionUpdate, DischargeRequest, BillingSummary


class AdmissionService:
    """Service class for admission business logic operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_admission(self, admission_data: AdmissionCreate) -> Admission:
        """
        Create a new admission.
        
        Args:
            admission_data: Admission creation data
            
        Returns:
            Created admission instance
            
        Raises:
            ValueError: If room is not available or patient already admitted
        """
        # Check if room is available
        room = self.db.query(Room).filter(Room.id == admission_data.room_id).first()
        if not room:
            raise ValueError(f"Room with ID {admission_data.room_id} not found")
        
        if not room.is_available():
            raise ValueError(f"Room {room.room_number} is not available for admission")
        
        # Check if patient already has active admission
        existing_admission = self.db.query(Admission).filter(
            and_(
                Admission.patient_id == admission_data.patient_id,
                Admission.status == AdmissionStatus.ACTIVE
            )
        ).first()
        
        if existing_admission:
            raise ValueError("Patient already has an active admission")
        
        # Validate patient exists and is eligible for admission
        self.validate_patient_for_admission(admission_data.patient_id)
        
        # Validate staff authorization
        self.validate_staff_authorization(admission_data.staff_id)
        
        # Create new admission
        admission = Admission(
            room_id=admission_data.room_id,
            patient_id=admission_data.patient_id,
            staff_id=admission_data.staff_id,
            admission_date=admission_data.admission_date,
            status=AdmissionStatus.ACTIVE
        )
        
        # Update room status to occupied
        room.status = RoomStatus.OCCUPIED
        
        self.db.add(admission)
        self.db.commit()
        self.db.refresh(admission)
        
        return admission
    
    def get_admission(self, admission_id: int) -> Optional[Admission]:
        """
        Get admission by ID.
        
        Args:
            admission_id: Admission ID
            
        Returns:
            Admission instance or None if not found
        """
        return self.db.query(Admission).filter(Admission.id == admission_id).first()
    
    def get_admissions(self, patient_id: Optional[str] = None, room_id: Optional[int] = None, 
                      status: Optional[AdmissionStatus] = None, skip: int = 0, limit: int = 100) -> List[Admission]:
        """
        Get admissions with optional filtering.
        
        Args:
            patient_id: Optional patient ID filter
            room_id: Optional room ID filter
            status: Optional status filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of admission instances
        """
        query = self.db.query(Admission)
        
        if patient_id:
            query = query.filter(Admission.patient_id == patient_id)
        if room_id:
            query = query.filter(Admission.room_id == room_id)
        if status:
            query = query.filter(Admission.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    def get_admissions_with_details(self, patient_id: Optional[str] = None, room_id: Optional[int] = None, 
                                   status: Optional[AdmissionStatus] = None, skip: int = 0, limit: int = 100) -> List[dict]:
        """
        Get admissions with patient and room details.
        
        Args:
            patient_id: Optional patient ID filter
            room_id: Optional room ID filter
            status: Optional status filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of admission dictionaries with details
        """
        from app.models.patient import Patient
        from app.models.staff import Staff
        
        # First get the admissions
        query = self.db.query(Admission)
        
        if patient_id:
            query = query.filter(Admission.patient_id == patient_id)
        if room_id:
            query = query.filter(Admission.room_id == room_id)
        if status:
            query = query.filter(Admission.status == status)
        
        admissions = query.offset(skip).limit(limit).all()
        
        # Convert to dictionary format with details
        result = []
        for admission in admissions:
            # Get room details
            room = self.db.query(Room).filter(Room.id == admission.room_id).first()
            
            # Get patient details - handle UUID conversion
            patient = None
            if admission.patient_id:
                try:
                    import uuid
                    # Handle different UUID formats
                    patient_id_str = str(admission.patient_id)
                    
                    # If it's a UUID with hyphens, convert to UUID object
                    if len(patient_id_str) == 36 and patient_id_str.count('-') == 4:
                        patient_uuid = uuid.UUID(patient_id_str)
                    # If it's a UUID without hyphens, add hyphens and convert
                    elif len(patient_id_str) == 32 and patient_id_str.count('-') == 0:
                        # Add hyphens to make it a proper UUID format
                        formatted_uuid = f"{patient_id_str[:8]}-{patient_id_str[8:12]}-{patient_id_str[12:16]}-{patient_id_str[16:20]}-{patient_id_str[20:]}"
                        patient_uuid = uuid.UUID(formatted_uuid)
                    else:
                        # Try to query directly with the string
                        patient = self.db.query(Patient).filter(Patient.id == patient_id_str).first()
                        continue
                    
                    patient = self.db.query(Patient).filter(Patient.id == patient_uuid).first()
                except (ValueError, TypeError) as e:
                    print(f"Error converting patient_id {admission.patient_id}: {e}")
                    # Try direct string query as fallback
                    try:
                        patient = self.db.query(Patient).filter(Patient.id == str(admission.patient_id)).first()
                    except:
                        patient = None
            
            # Get staff details - handle UUID conversion
            staff = None
            if admission.staff_id:
                try:
                    import uuid
                    # Handle different UUID formats
                    staff_id_str = str(admission.staff_id)
                    
                    # If it's a UUID with hyphens, convert to UUID object
                    if len(staff_id_str) == 36 and staff_id_str.count('-') == 4:
                        staff_uuid = uuid.UUID(staff_id_str)
                    # If it's a UUID without hyphens, add hyphens and convert
                    elif len(staff_id_str) == 32 and staff_id_str.count('-') == 0:
                        # Add hyphens to make it a proper UUID format
                        formatted_uuid = f"{staff_id_str[:8]}-{staff_id_str[8:12]}-{staff_id_str[12:16]}-{staff_id_str[16:20]}-{staff_id_str[20:]}"
                        staff_uuid = uuid.UUID(formatted_uuid)
                    else:
                        # Try to query directly with the string
                        staff = self.db.query(Staff).filter(Staff.id == staff_id_str).first()
                        continue
                    
                    staff = self.db.query(Staff).filter(Staff.id == staff_uuid).first()
                except (ValueError, TypeError) as e:
                    print(f"Error converting staff_id {admission.staff_id}: {e}")
                    # Try direct string query as fallback
                    try:
                        staff = self.db.query(Staff).filter(Staff.id == str(admission.staff_id)).first()
                    except:
                        staff = None
            
            admission_dict = {
                'id': admission.id,
                'room_id': admission.room_id,
                'patient_id': admission.patient_id,
                'staff_id': admission.staff_id,
                'admission_date': admission.admission_date,
                'discharge_date': admission.discharge_date,
                'discharge_reason': admission.discharge_reason,
                'discharge_notes': admission.discharge_notes,
                'invoice_id': admission.invoice_id,
                'status': admission.status,
                'created_at': admission.created_at,
                'updated_at': admission.updated_at,
                'room': {
                    'id': room.id if room else None,
                    'room_number': room.room_number if room else None,
                    'type': room.type if room else None,
                    'status': room.status if room else None,
                    'daily_rate_cents': room.daily_rate_cents if room else None
                } if room else None,
                'patient': {
                    'id': patient.id if patient else None,
                    'name': patient.name if patient else None,
                    'email': patient.email if patient else None,
                    'phone': patient.phone if patient else None
                } if patient else None,
                'staff': {
                    'id': staff.id if staff else None,
                    'name': staff.name if staff else None,
                    'email': staff.email if staff else None,
                    'role': staff.role if staff else None
                } if staff else None
            }
            result.append(admission_dict)
        
        return result
    
    def get_active_admissions(self, skip: int = 0, limit: int = 100) -> List[Admission]:
        """
        Get active admissions.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active admission instances
        """
        return self.get_admissions(status=AdmissionStatus.ACTIVE, skip=skip, limit=limit)
    
    def discharge_patient(self, admission_id: int, discharge_data: DischargeRequest) -> dict:
        """
        Discharge a patient and calculate billing.
        
        Args:
            admission_id: Admission ID
            discharge_data: Discharge request data
            
        Returns:
            Dictionary with admission, invoice, and billing summary
            
        Raises:
            ValueError: If admission cannot be discharged
        """
        admission = self.get_admission(admission_id)
        if not admission:
            raise ValueError(f"Admission with ID {admission_id} not found")
        
        if not admission.can_be_discharged():
            raise ValueError("Admission cannot be discharged")
        
        # Validate discharge request
        self._validate_discharge_request(discharge_data)
        
        # Set discharge date and additional information
        discharge_date = discharge_data.discharge_date or datetime.now()
        admission.discharge_date = discharge_date
        admission.discharge_reason = getattr(discharge_data, 'discharge_reason', None)
        admission.discharge_notes = getattr(discharge_data, 'discharge_notes', None)
        admission.status = AdmissionStatus.DISCHARGED
        
        # Update room status to available
        room = self.db.query(Room).filter(Room.id == admission.room_id).first()
        if room:
            room.status = RoomStatus.AVAILABLE
        
        # Calculate billing
        billing_summary = self._calculate_billing(admission)
        
        # Create invoice (placeholder - would integrate with existing billing system)
        invoice = self._create_invoice(admission, billing_summary)
        admission.invoice_id = invoice['id']
        
        self.db.commit()
        self.db.refresh(admission)
        
        return {
            'admission': admission,
            'invoice': invoice,
            'billing_summary': billing_summary
        }
    
    def _validate_discharge_request(self, discharge_data: DischargeRequest) -> None:
        """
        Validate discharge request data.
        
        Args:
            discharge_data: Discharge request data
            
        Raises:
            ValueError: If discharge request is invalid
        """
        if discharge_data.discharge_date:
            # Validate discharge date is reasonable (allow up to 7 days in future for planned discharges)
            max_future = datetime.now() + timedelta(days=7)
            if discharge_data.discharge_date > max_future:
                raise ValueError("Discharge date cannot be more than 7 days in the future")
            
            # Validate discharge date is not too far in the past
            if discharge_data.discharge_date < datetime.now() - timedelta(days=30):
                raise ValueError("Discharge date cannot be more than 30 days in the past")
        
        # Validate discharge reason if provided
        if hasattr(discharge_data, 'discharge_reason') and discharge_data.discharge_reason:
            valid_reasons = ['recovery', 'transfer', 'patient_request', 'medical_necessity', 'other']
            if discharge_data.discharge_reason not in valid_reasons:
                raise ValueError(f"Invalid discharge reason. Must be one of: {', '.join(valid_reasons)}")
        
        # Validate discharge notes if provided
        if hasattr(discharge_data, 'discharge_notes') and discharge_data.discharge_notes:
            if len(discharge_data.discharge_notes) > 500:
                raise ValueError("Discharge notes cannot exceed 500 characters")
    
    def update_admission(self, admission_id: int, admission_data: AdmissionUpdate) -> Optional[Admission]:
        """
        Update admission details.
        
        Args:
            admission_id: Admission ID
            admission_data: Admission update data
            
        Returns:
            Updated admission instance or None if not found
        """
        admission = self.get_admission(admission_id)
        if not admission:
            return None
        
        # Update fields
        if admission_data.discharge_date is not None:
            admission.discharge_date = admission_data.discharge_date
        
        self.db.commit()
        self.db.refresh(admission)
        
        return admission
    
    def get_admission_count(self, patient_id: Optional[str] = None, room_id: Optional[int] = None, 
                           status: Optional[AdmissionStatus] = None) -> int:
        """
        Get total count of admissions matching filters.
        
        Args:
            patient_id: Optional patient ID filter
            room_id: Optional room ID filter
            status: Optional status filter
            
        Returns:
            Total count of admissions
        """
        query = self.db.query(Admission)
        
        if patient_id:
            query = query.filter(Admission.patient_id == patient_id)
        if room_id:
            query = query.filter(Admission.room_id == room_id)
        if status:
            query = query.filter(Admission.status == status)
        
        return query.count()
    
    def _calculate_billing(self, admission: Admission) -> BillingSummary:
        """
        Calculate billing for admission.
        
        Args:
            admission: Admission instance
            
        Returns:
            Billing summary with charges
        """
        if not admission.discharge_date:
            raise ValueError("Cannot calculate billing without discharge date")
        
        # Get room daily rate
        room = self.db.query(Room).filter(Room.id == admission.room_id).first()
        if not room:
            raise ValueError("Room not found for billing calculation")
        
        daily_rate_cents = room.daily_rate_cents
        
        # Calculate duration
        duration_hours = admission.get_duration_hours()
        duration_days = admission.get_duration_days()
        
        # Determine if same day admission/discharge
        is_same_day = admission.admission_date.date() == admission.discharge_date.date()
        
        # Calculate charges based on business rules
        if is_same_day:
            # Same day: hourly rate (daily rate / 24)
            hourly_rate_cents = daily_rate_cents / 24
            total_charges_cents = int(duration_hours * hourly_rate_cents)
        else:
            # Multi-day: full daily rate for each day
            total_charges_cents = int(duration_days * daily_rate_cents)
        
        return BillingSummary(
            daily_rate_cents=daily_rate_cents,
            days_stayed=duration_days,
            total_charges_cents=total_charges_cents,
            is_same_day=is_same_day
        )
    
    def _create_invoice(self, admission: Admission, billing_summary: BillingSummary) -> dict:
        """
        Create invoice for admission (placeholder implementation).
        
        Args:
            admission: Admission instance
            billing_summary: Billing calculation summary
            
        Returns:
            Invoice details dictionary
        """
        # This would integrate with existing billing system
        # For now, return a placeholder invoice with integer ID
        invoice_id = int(datetime.now().timestamp())
        return {
            'id': invoice_id,
            'patient_id': admission.patient_id,
            'total_amount_cents': billing_summary.total_charges_cents,
            'status': 'pending',
            'created_at': datetime.now()
        }
    
    def validate_patient_for_admission(self, patient_id: str) -> dict:
        """
        Validate patient eligibility for admission.
        
        Args:
            patient_id: Patient ID to validate
            
        Returns:
            Dictionary with patient validation details
            
        Raises:
            ValueError: If patient is not eligible for admission
        """
        # Check if patient exists
        # Note: This assumes a Patient model exists in the system
        # For now, we'll create a mock validation
        patient = self._get_patient_by_id(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        # Check if patient is already admitted
        existing_admission = self.db.query(Admission).filter(
            and_(
                Admission.patient_id == patient_id,
                Admission.status == AdmissionStatus.ACTIVE
            )
        ).first()
        
        if existing_admission:
            raise ValueError(f"Patient {patient_id} already has an active admission")
        
        # Check patient status (assuming patient has a status field)
        if hasattr(patient, 'status') and patient.status not in ['active', 'eligible']:
            raise ValueError(f"Patient {patient_id} is not eligible for admission (status: {patient.status})")
        
        # Check if patient has outstanding bills (optional business rule)
        if hasattr(patient, 'outstanding_balance') and patient.outstanding_balance > 0:
            # This could be a warning rather than an error depending on business rules
            pass
        
        return {
            'patient_id': patient_id,
            'eligible': True,
            'patient_name': getattr(patient, 'name', 'Unknown'),
            'patient_status': getattr(patient, 'status', 'active')
        }
    
    def _get_patient_by_id(self, patient_id: str):
        """
        Get patient by ID.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Patient instance or None if not found
        """
        # This is a placeholder implementation
        # In a real system, this would query the Patient model
        # For now, we'll return a mock patient object
        class MockPatient:
            def __init__(self, patient_id):
                self.id = patient_id
                self.name = f"Patient {patient_id}"
                self.status = "active"
                self.outstanding_balance = 0
        
        # Mock validation - in real system, query actual Patient table
        if patient_id and len(patient_id) > 0:
            return MockPatient(patient_id)
        return None
    
    def get_patient_admission_history(self, patient_id: str) -> List[Admission]:
        """
        Get patient's admission history.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            List of admission instances for the patient
        """
        return self.db.query(Admission).filter(
            Admission.patient_id == patient_id
        ).order_by(Admission.admission_date.desc()).all()
    
    def check_patient_eligibility(self, patient_id: str) -> dict:
        """
        Check if patient is eligible for admission.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Dictionary with eligibility status and details
        """
        try:
            validation_result = self.validate_patient_for_admission(patient_id)
            return {
                'eligible': True,
                'patient_id': patient_id,
                'details': validation_result
            }
        except ValueError as e:
            return {
                'eligible': False,
                'patient_id': patient_id,
                'reason': str(e)
            }
    
    def validate_staff_authorization(self, staff_id: str) -> dict:
        """
        Validate staff authorization for admission operations.
        
        Args:
            staff_id: Staff ID to validate
            
        Returns:
            Dictionary with staff validation details
            
        Raises:
            ValueError: If staff is not authorized for admission operations
        """
        # Check if staff exists
        staff = self._get_staff_by_id(staff_id)
        if not staff:
            raise ValueError(f"Staff with ID {staff_id} not found")
        
        # Check staff status
        if hasattr(staff, 'status') and staff.status not in ['active', 'on_duty']:
            raise ValueError(f"Staff {staff_id} is not active (status: {staff.status})")
        
        # Check staff role permissions
        if hasattr(staff, 'role'):
            authorized_roles = ['doctor', 'nurse', 'admin', 'receptionist']
            if staff.role not in authorized_roles:
                raise ValueError(f"Staff {staff_id} with role '{staff.role}' is not authorized for admission operations")
        
        # Check if staff is on duty (optional business rule)
        if hasattr(staff, 'shift_status') and staff.shift_status != 'on_duty':
            # This could be a warning rather than an error depending on business rules
            pass
        
        return {
            'staff_id': staff_id,
            'authorized': True,
            'staff_name': getattr(staff, 'name', 'Unknown'),
            'role': getattr(staff, 'role', 'unknown'),
            'status': getattr(staff, 'status', 'active')
        }
    
    def _get_staff_by_id(self, staff_id: str):
        """
        Get staff by ID.
        
        Args:
            staff_id: Staff ID
            
        Returns:
            Staff instance or None if not found
        """
        # This is a placeholder implementation
        # In a real system, this would query the Staff model
        # For now, we'll return a mock staff object
        class MockStaff:
            def __init__(self, staff_id):
                self.id = staff_id
                self.name = f"Staff {staff_id}"
                self.role = "nurse" if len(staff_id) % 2 == 0 else "doctor"
                self.status = "active"
                self.shift_status = "on_duty"
        
        # Mock validation - in real system, query actual Staff table
        if staff_id and len(staff_id) > 0:
            return MockStaff(staff_id)
        return None
    
    def check_staff_authorization(self, staff_id: str) -> dict:
        """
        Check if staff is authorized for admission operations.
        
        Args:
            staff_id: Staff ID
            
        Returns:
            Dictionary with authorization status and details
        """
        try:
            validation_result = self.validate_staff_authorization(staff_id)
            return {
                'authorized': True,
                'staff_id': staff_id,
                'details': validation_result
            }
        except ValueError as e:
            return {
                'authorized': False,
                'staff_id': staff_id,
                'reason': str(e)
            }
    
    def get_staff_admission_permissions(self, staff_id: str) -> dict:
        """
        Get staff admission permissions.
        
        Args:
            staff_id: Staff ID
            
        Returns:
            Dictionary with staff permissions
        """
        staff = self._get_staff_by_id(staff_id)
        if not staff:
            return {
                'can_admit': False,
                'can_discharge': False,
                'can_view_all': False,
                'reason': 'Staff not found'
            }
        
        role = getattr(staff, 'role', 'unknown')
        
        # Define role-based permissions
        permissions = {
            'doctor': {
                'can_admit': True,
                'can_discharge': True,
                'can_view_all': True
            },
            'nurse': {
                'can_admit': True,
                'can_discharge': False,
                'can_view_all': True
            },
            'admin': {
                'can_admit': True,
                'can_discharge': True,
                'can_view_all': True
            },
            'receptionist': {
                'can_admit': True,
                'can_discharge': False,
                'can_view_all': False
            }
        }
        
        return permissions.get(role, {
            'can_admit': False,
            'can_discharge': False,
            'can_view_all': False,
            'reason': f'Unknown role: {role}'
        })
    
    def validate_room_availability(self, room_id: int) -> dict:
        """
        Validate if a room is available for admission.
        
        Args:
            room_id: Room ID to validate
            
        Returns:
            Dictionary with availability status and details
        """
        room = self.db.query(Room).filter(Room.id == room_id).first()
        if not room:
            return {
                'available': False,
                'reason': f'Room {room_id} not found'
            }
        
        if not room.is_available():
            return {
                'available': False,
                'reason': f'Room {room.room_number} is not available (status: {room.status})'
            }
        
        return {
            'available': True,
            'room_number': room.room_number,
            'room_type': room.type.value if hasattr(room.type, 'value') else str(room.type)
        }

    def get_admission_statistics(self) -> dict:
        """
        Get admission statistics for dashboard.
        
        Returns:
            Dictionary with admission statistics
        """
        total_admissions = self.db.query(Admission).count()
        active_admissions = self.db.query(Admission).filter(Admission.status == AdmissionStatus.ACTIVE).count()
        discharged_admissions = self.db.query(Admission).filter(Admission.status == AdmissionStatus.DISCHARGED).count()
        
        # Calculate average length of stay for discharged admissions
        discharged_with_duration = self.db.query(Admission).filter(
            and_(
                Admission.status == AdmissionStatus.DISCHARGED,
                Admission.discharge_date.isnot(None)
            )
        ).all()
        
        avg_length_of_stay = 0
        if discharged_with_duration:
            total_hours = sum(admission.get_duration_hours() for admission in discharged_with_duration)
            avg_length_of_stay = total_hours / len(discharged_with_duration)
        
        # Get admissions by room type
        from app.models.room import Room, RoomType
        room_type_stats = {}
        for room_type in RoomType:
            count = self.db.query(Admission).join(Room).filter(
                and_(
                    Room.type == room_type,
                    Admission.status == AdmissionStatus.ACTIVE
                )
            ).count()
            room_type_stats[room_type.value] = count
        
        # Get recent admissions (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_admissions = self.db.query(Admission).filter(
            Admission.admission_date >= week_ago
        ).count()
        
        return {
            'total_admissions': total_admissions,
            'active_admissions': active_admissions,
            'discharged_admissions': discharged_admissions,
            'average_length_of_stay_hours': round(avg_length_of_stay, 2),
            'average_length_of_stay_days': round(avg_length_of_stay / 24, 2),
            'recent_admissions_7_days': recent_admissions,
            'room_type_breakdown': room_type_stats,
            'occupancy_rate': (active_admissions / total_admissions * 100) if total_admissions > 0 else 0
        }

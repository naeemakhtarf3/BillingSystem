from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, validator, Field
from datetime import datetime, date
import re
import phonenumbers
from email_validator import validate_email, EmailNotValidError

class ValidationError(Exception):
    """Custom validation error with detailed information."""
    
    def __init__(self, field: str, value: Any, message: str):
        self.field = field
        self.value = value
        self.message = message
        super().__init__(f"Validation error for {field}: {message}")

class InputValidator:
    """Comprehensive input validation utilities."""
    
    @staticmethod
    def validate_room_number(room_number: str) -> bool:
        """Validate room number format."""
        if not room_number or len(room_number.strip()) == 0:
            raise ValidationError("room_number", room_number, "Room number cannot be empty")
        
        # Allow alphanumeric with optional hyphens and spaces
        pattern = r'^[A-Za-z0-9\-\s]+$'
        if not re.match(pattern, room_number):
            raise ValidationError("room_number", room_number, "Room number can only contain letters, numbers, hyphens, and spaces")
        
        if len(room_number) > 50:
            raise ValidationError("room_number", room_number, "Room number cannot exceed 50 characters")
        
        return True
    
    @staticmethod
    def validate_daily_rate(rate: Union[int, float]) -> bool:
        """Validate daily rate value."""
        if rate is None:
            raise ValidationError("daily_rate", rate, "Daily rate is required")
        
        if not isinstance(rate, (int, float)):
            raise ValidationError("daily_rate", rate, "Daily rate must be a number")
        
        if rate < 0:
            raise ValidationError("daily_rate", rate, "Daily rate cannot be negative")
        
        if rate > 1000000:  # $10,000 per day max
            raise ValidationError("daily_rate", rate, "Daily rate cannot exceed $10,000 per day")
        
        return True
    
    @staticmethod
    def validate_patient_id(patient_id: Union[int, str]) -> bool:
        """Validate patient ID format."""
        if patient_id is None:
            raise ValidationError("patient_id", patient_id, "Patient ID is required")
        
        # Convert to int if possible
        try:
            patient_id = int(patient_id)
        except (ValueError, TypeError):
            raise ValidationError("patient_id", patient_id, "Patient ID must be a valid integer")
        
        if patient_id <= 0:
            raise ValidationError("patient_id", patient_id, "Patient ID must be positive")
        
        return True
    
    @staticmethod
    def validate_staff_id(staff_id: Union[int, str]) -> bool:
        """Validate staff ID format."""
        if staff_id is None:
            raise ValidationError("staff_id", staff_id, "Staff ID is required")
        
        # Convert to int if possible
        try:
            staff_id = int(staff_id)
        except (ValueError, TypeError):
            raise ValidationError("staff_id", staff_id, "Staff ID must be a valid integer")
        
        if staff_id <= 0:
            raise ValidationError("staff_id", staff_id, "Staff ID must be positive")
        
        return True
    
    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
        """Validate date range logic."""
        if start_date is None or end_date is None:
            raise ValidationError("date_range", (start_date, end_date), "Both start and end dates are required")
        
        if start_date >= end_date:
            raise ValidationError("date_range", (start_date, end_date), "Start date must be before end date")
        
        # Check if dates are not too far in the future
        max_future_date = datetime.now().replace(year=datetime.now().year + 1)
        if start_date > max_future_date or end_date > max_future_date:
            raise ValidationError("date_range", (start_date, end_date), "Dates cannot be more than 1 year in the future")
        
        return True
    
    @staticmethod
    def validate_email_address(email: str) -> bool:
        """Validate email address format."""
        if not email or len(email.strip()) == 0:
            raise ValidationError("email", email, "Email address is required")
        
        try:
            validate_email(email)
            return True
        except EmailNotValidError as e:
            raise ValidationError("email", email, f"Invalid email format: {str(e)}")
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Validate phone number format."""
        if not phone or len(phone.strip()) == 0:
            raise ValidationError("phone", phone, "Phone number is required")
        
        try:
            # Parse phone number (assuming US format)
            parsed_phone = phonenumbers.parse(phone, "US")
            if not phonenumbers.is_valid_number(parsed_phone):
                raise ValidationError("phone", phone, "Invalid phone number format")
            return True
        except Exception as e:
            raise ValidationError("phone", phone, f"Invalid phone number: {str(e)}")
    
    @staticmethod
    def validate_text_length(text: str, field_name: str, max_length: int = 500, min_length: int = 0) -> bool:
        """Validate text length constraints."""
        if text is None:
            text = ""
        
        if len(text) < min_length:
            raise ValidationError(field_name, text, f"{field_name} must be at least {min_length} characters")
        
        if len(text) > max_length:
            raise ValidationError(field_name, text, f"{field_name} cannot exceed {max_length} characters")
        
        return True
    
    @staticmethod
    def validate_enum_value(value: Any, field_name: str, allowed_values: List[str]) -> bool:
        """Validate enum-like values."""
        if value is None:
            raise ValidationError(field_name, value, f"{field_name} is required")
        
        if value not in allowed_values:
            raise ValidationError(field_name, value, f"{field_name} must be one of: {', '.join(allowed_values)}")
        
        return True

class EnhancedValidationMixin:
    """Mixin for enhanced validation in Pydantic models."""
    
    @validator('*', pre=True)
    def validate_all_fields(cls, v, field):
        """Validate all fields with enhanced error messages."""
        field_name = field.name
        
        # Skip validation for None values (handled by required validators)
        if v is None:
            return v
        
        # Apply field-specific validation
        if field_name == 'room_number':
            InputValidator.validate_room_number(v)
        elif field_name == 'daily_rate_cents':
            InputValidator.validate_daily_rate(v)
        elif field_name == 'patient_id':
            InputValidator.validate_patient_id(v)
        elif field_name == 'staff_id':
            InputValidator.validate_staff_id(v)
        elif field_name in ['description', 'notes', 'discharge_notes']:
            InputValidator.validate_text_length(v, field_name, max_length=1000)
        
        return v

class ValidationResponse(BaseModel):
    """Standard validation response format."""
    
    is_valid: bool
    errors: List[Dict[str, Any]] = []
    warnings: List[str] = []
    
    def add_error(self, field: str, message: str, value: Any = None):
        """Add validation error."""
        self.errors.append({
            'field': field,
            'message': message,
            'value': value
        })
        self.is_valid = False
    
    def add_warning(self, message: str):
        """Add validation warning."""
        self.warnings.append(message)

def validate_request_data(data: Dict[str, Any], validation_rules: Dict[str, Any]) -> ValidationResponse:
    """Validate request data against rules."""
    response = ValidationResponse(is_valid=True)
    
    for field, rules in validation_rules.items():
        value = data.get(field)
        
        try:
            # Required field validation
            if rules.get('required', False) and (value is None or value == ''):
                response.add_error(field, f"{field} is required")
                continue
            
            # Skip validation for empty optional fields
            if not rules.get('required', False) and (value is None or value == ''):
                continue
            
            # Type validation
            expected_type = rules.get('type')
            if expected_type and not isinstance(value, expected_type):
                response.add_error(field, f"{field} must be of type {expected_type.__name__}")
                continue
            
            # Range validation
            if 'min' in rules and value < rules['min']:
                response.add_error(field, f"{field} must be at least {rules['min']}")
            
            if 'max' in rules and value > rules['max']:
                response.add_error(field, f"{field} must be at most {rules['max']}")
            
            # Length validation
            if 'min_length' in rules and len(str(value)) < rules['min_length']:
                response.add_error(field, f"{field} must be at least {rules['min_length']} characters")
            
            if 'max_length' in rules and len(str(value)) > rules['max_length']:
                response.add_error(field, f"{field} must be at most {rules['max_length']} characters")
            
            # Pattern validation
            if 'pattern' in rules:
                if not re.match(rules['pattern'], str(value)):
                    response.add_error(field, f"{field} format is invalid")
            
            # Custom validation
            if 'custom_validator' in rules:
                rules['custom_validator'](value)
                
        except ValidationError as e:
            response.add_error(field, e.message, e.value)
        except Exception as e:
            response.add_error(field, f"Validation error: {str(e)}")
    
    return response

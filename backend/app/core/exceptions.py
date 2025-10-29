"""
Custom exception classes and error handling middleware.

This module provides structured error handling for the patient admission
and discharge workflow with consistent error responses.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import Dict, Any, Optional
import logging
import traceback

logger = logging.getLogger(__name__)

class AdmissionWorkflowException(Exception):
    """Base exception for admission workflow errors."""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or "ADMISSION_ERROR"
        self.details = details or {}
        super().__init__(self.message)

class RoomNotAvailableException(AdmissionWorkflowException):
    """Exception raised when room is not available for admission."""
    def __init__(self, room_id: int, message: str = None):
        super().__init__(
            message or f"Room {room_id} is not available for admission",
            "ROOM_NOT_AVAILABLE",
            {"room_id": room_id}
        )

class PatientAlreadyAdmittedException(AdmissionWorkflowException):
    """Exception raised when patient is already admitted."""
    def __init__(self, patient_id: int, message: str = None):
        super().__init__(
            message or f"Patient {patient_id} is already admitted",
            "PATIENT_ALREADY_ADMITTED",
            {"patient_id": patient_id}
        )

class RoomOccupiedException(AdmissionWorkflowException):
    """Exception raised when trying to admit to an occupied room."""
    def __init__(self, room_id: int, message: str = None):
        super().__init__(
            message or f"Room {room_id} is currently occupied",
            "ROOM_OCCUPIED",
            {"room_id": room_id}
        )

class InvalidStatusTransitionException(AdmissionWorkflowException):
    """Exception raised for invalid status transitions."""
    def __init__(self, current_status: str, new_status: str, message: str = None):
        super().__init__(
            message or f"Invalid status transition from {current_status} to {new_status}",
            "INVALID_STATUS_TRANSITION",
            {"current_status": current_status, "new_status": new_status}
        )

class ConcurrencyException(AdmissionWorkflowException):
    """Exception raised for concurrency conflicts."""
    def __init__(self, resource_id: int, message: str = None):
        super().__init__(
            message or f"Concurrency conflict for resource {resource_id}",
            "CONCURRENCY_CONFLICT",
            {"resource_id": resource_id}
        )

class ValidationException(AdmissionWorkflowException):
    """Exception raised for validation errors."""
    def __init__(self, field: str, value: Any, message: str = None):
        super().__init__(
            message or f"Validation error for field {field}: {value}",
            "VALIDATION_ERROR",
            {"field": field, "value": value}
        )

def create_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: Dict[str, Any] = None,
    request_id: str = None
) -> JSONResponse:
    """Create a structured error response."""
    error_data = {
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {},
            "timestamp": None,  # Will be set by middleware
            "request_id": request_id
        }
    }
    
    return JSONResponse(
        status_code=status_code,
        content=error_data
    )

async def admission_workflow_exception_handler(request: Request, exc: AdmissionWorkflowException) -> JSONResponse:
    """Handle admission workflow exceptions."""
    logger.error(f"Admission workflow error: {exc.message}", extra={
        "error_code": exc.error_code,
        "details": exc.details,
        "path": request.url.path,
        "method": request.method
    })
    
    return create_error_response(
        status_code=400,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation exceptions."""
    logger.warning(f"Validation error: {exc.errors()}", extra={
        "path": request.url.path,
        "method": request.method
    })
    
    # Format validation errors
    formatted_errors = []
    for error in exc.errors():
        formatted_errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return create_error_response(
        status_code=422,
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"validation_errors": formatted_errors}
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP exception: {exc.detail}", extra={
        "status_code": exc.status_code,
        "path": request.url.path,
        "method": request.method
    })
    
    return create_error_response(
        status_code=exc.status_code,
        error_code="HTTP_ERROR",
        message=exc.detail
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy exceptions."""
    logger.error(f"Database error: {str(exc)}", extra={
        "path": request.url.path,
        "method": request.method
    }, exc_info=True)
    
    # Handle specific SQLAlchemy errors
    if isinstance(exc, IntegrityError):
        return create_error_response(
            status_code=409,
            error_code="INTEGRITY_ERROR",
            message="Database integrity constraint violation",
            details={"constraint": str(exc.orig) if hasattr(exc, 'orig') else None}
        )
    
    return create_error_response(
        status_code=500,
        error_code="DATABASE_ERROR",
        message="Database operation failed"
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", extra={
        "path": request.url.path,
        "method": request.method
    }, exc_info=True)
    
    return create_error_response(
        status_code=500,
        error_code="INTERNAL_ERROR",
        message="An unexpected error occurred"
    )

def setup_exception_handlers(app):
    """Setup exception handlers for the FastAPI app."""
    app.add_exception_handler(AdmissionWorkflowException, admission_workflow_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

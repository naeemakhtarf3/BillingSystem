"""
Comprehensive API Documentation for Clinic Billing System

This module provides detailed documentation for all API endpoints,
including request/response schemas, error codes, and usage examples.
"""

from typing import Dict, List, Any
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def create_detailed_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """Create detailed OpenAPI schema with comprehensive documentation."""
    
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Clinic Billing System API",
        version="1.0.0",
        description="""
        # Clinic Billing System API

        A comprehensive healthcare management system for patient admissions, 
        room management, and billing operations.

        ## Features

        - **Patient Management**: Complete patient admission and discharge workflows
        - **Room Management**: Real-time room status tracking and maintenance scheduling
        - **Billing System**: Automated billing calculation with detailed breakdowns
        - **Real-time Updates**: WebSocket integration for live status updates
        - **Role-based Access**: Secure access control for different user types

        ## Authentication

        The API uses JWT-based authentication. Include the token in the Authorization header:

        ```
        Authorization: Bearer <your-jwt-token>
        ```

        ## Rate Limiting

        - Standard endpoints: 100 requests per minute
        - Search endpoints: 50 requests per minute
        - Admin endpoints: 20 requests per minute

        ## Error Handling

        All endpoints return consistent error responses:

        ```json
        {
            "error": "Error type",
            "detail": "Detailed error message",
            "status_code": 400
        }
        ```

        ## Common Error Codes

        - `400`: Bad Request - Invalid input data
        - `401`: Unauthorized - Invalid or missing authentication
        - `403`: Forbidden - Insufficient permissions
        - `404`: Not Found - Resource not found
        - `409`: Conflict - Resource already exists or cannot be modified
        - `422`: Unprocessable Entity - Validation errors
        - `500`: Internal Server Error - Server-side error

        ## WebSocket Events

        The system provides real-time updates via WebSocket:

        - `room_status_update`: Room status changes
        - `admission_update`: Admission status changes
        - `billing_update`: Billing calculation updates

        ## Data Models

        ### Room
        - `id`: Unique identifier
        - `room_number`: Human-readable room identifier
        - `type`: Room type (standard, private, icu)
        - `status`: Current status (available, occupied, maintenance)
        - `daily_rate_cents`: Daily rate in cents
        - `created_at`: Creation timestamp
        - `updated_at`: Last update timestamp

        ### Admission
        - `id`: Unique identifier
        - `room_id`: Reference to room
        - `patient_id`: Reference to patient
        - `staff_id`: Reference to staff member
        - `admission_date`: Admission timestamp
        - `discharge_date`: Discharge timestamp (nullable)
        - `status`: Current status (active, discharged)
        - `invoice_id`: Reference to generated invoice

        ## Usage Examples

        ### Create a new admission

        ```bash
        curl -X POST "https://api.clinic-billing.com/api/v1/admissions" \\
          -H "Authorization: Bearer <token>" \\
          -H "Content-Type: application/json" \\
          -d '{
            "patient_id": 123,
            "room_id": 456,
            "staff_id": 789,
            "admission_date": "2024-01-15T10:00:00Z"
          }'
        ```

        ### Get available rooms

        ```bash
        curl -X GET "https://api.clinic-billing.com/api/v1/rooms/available/list" \\
          -H "Authorization: Bearer <token>"
        ```

        ### Discharge a patient

        ```bash
        curl -X POST "https://api.clinic-billing.com/api/v1/admissions/123/discharge" \\
          -H "Authorization: Bearer <token>" \\
          -H "Content-Type: application/json" \\
          -d '{
            "discharge_date": "2024-01-16T14:00:00Z",
            "discharge_reason": "recovery",
            "discharge_notes": "Patient fully recovered"
          }'
        ```

        ## Performance Considerations

        - Database queries are optimized with proper indexing
        - Pagination is implemented for large datasets
        - Caching is used for frequently accessed data
        - Connection pooling is configured for optimal performance

        ## Security

        - All endpoints require authentication
        - Role-based access control is enforced
        - Input validation prevents injection attacks
        - CORS is properly configured
        - Rate limiting prevents abuse

        ## Monitoring

        - All API calls are logged
        - Performance metrics are tracked
        - Error rates are monitored
        - System health is continuously checked

        ## Support

        For technical support or questions:
        - Email: support@clinic-billing.com
        - Documentation: https://docs.clinic-billing.com
        - Status Page: https://status.clinic-billing.com
        """,
        routes=app.routes,
    )

    # Add detailed tags
    openapi_schema["tags"] = [
        {
            "name": "Rooms",
            "description": "Room management operations including status updates and maintenance scheduling"
        },
        {
            "name": "Admissions", 
            "description": "Patient admission and discharge workflows with billing integration"
        },
        {
            "name": "Billing",
            "description": "Billing calculation and invoice management"
        },
        {
            "name": "Authentication",
            "description": "User authentication and authorization"
        },
        {
            "name": "Health",
            "description": "System health and monitoring endpoints"
        }
    ]

    # Add detailed examples
    openapi_schema["components"]["examples"] = {
        "RoomExample": {
            "summary": "Standard Room",
            "value": {
                "id": 1,
                "room_number": "101A",
                "type": "standard",
                "status": "available",
                "daily_rate_cents": 15000,
                "created_at": "2024-01-15T08:00:00Z",
                "updated_at": "2024-01-15T08:00:00Z"
            }
        },
        "AdmissionExample": {
            "summary": "Active Admission",
            "value": {
                "id": 1,
                "room_id": 1,
                "patient_id": 123,
                "staff_id": 456,
                "admission_date": "2024-01-15T10:00:00Z",
                "discharge_date": None,
                "status": "active",
                "invoice_id": None
            }
        },
        "BillingExample": {
            "summary": "Billing Summary",
            "value": {
                "total_charges_cents": 45000,
                "duration_hours": 72.5,
                "daily_rate_cents": 15000,
                "base_charges_cents": 45000,
                "additional_charges_cents": 0,
                "taxes_cents": 3825
            }
        }
    }

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token for authentication"
        }
    }

    # Add global security
    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

def add_endpoint_documentation(app: FastAPI):
    """Add comprehensive documentation to all endpoints."""
    
    # Add custom documentation routes
    @app.get("/docs/health", tags=["Health"])
    async def health_documentation():
        """Health check endpoint documentation."""
        return {
            "endpoint": "/health",
            "method": "GET",
            "description": "Check system health and database connectivity",
            "response": {
                "status": "healthy|degraded|unhealthy",
                "database": "connected|error",
                "timestamp": "ISO 8601 timestamp"
            }
        }
    
    @app.get("/docs/rooms", tags=["Documentation"])
    async def rooms_documentation():
        """Rooms API documentation."""
        return {
            "endpoints": [
                {
                    "path": "/api/v1/rooms",
                    "methods": ["GET", "POST"],
                    "description": "List and create rooms"
                },
                {
                    "path": "/api/v1/rooms/{room_id}",
                    "methods": ["GET", "PUT", "DELETE"],
                    "description": "Get, update, or delete specific room"
                },
                {
                    "path": "/api/v1/rooms/available/list",
                    "methods": ["GET"],
                    "description": "Get available rooms for admission"
                }
            ]
        }
    
    @app.get("/docs/admissions", tags=["Documentation"])
    async def admissions_documentation():
        """Admissions API documentation."""
        return {
            "endpoints": [
                {
                    "path": "/api/v1/admissions",
                    "methods": ["GET", "POST"],
                    "description": "List and create admissions"
                },
                {
                    "path": "/api/v1/admissions/{admission_id}",
                    "methods": ["GET", "PUT", "DELETE"],
                    "description": "Get, update, or delete specific admission"
                },
                {
                    "path": "/api/v1/admissions/{admission_id}/discharge",
                    "methods": ["POST"],
                    "description": "Discharge patient and calculate billing"
                }
            ]
        }

# API Usage Statistics
API_USAGE_STATS = {
    "total_requests": 0,
    "endpoints": {},
    "error_rates": {},
    "response_times": {}
}

def track_api_usage(endpoint: str, method: str, response_time: float, status_code: int):
    """Track API usage statistics."""
    API_USAGE_STATS["total_requests"] += 1
    
    key = f"{method} {endpoint}"
    if key not in API_USAGE_STATS["endpoints"]:
        API_USAGE_STATS["endpoints"][key] = 0
    API_USAGE_STATS["endpoints"][key] += 1
    
    if status_code >= 400:
        if key not in API_USAGE_STATS["error_rates"]:
            API_USAGE_STATS["error_rates"][key] = 0
        API_USAGE_STATS["error_rates"][key] += 1
    
    if key not in API_USAGE_STATS["response_times"]:
        API_USAGE_STATS["response_times"][key] = []
    API_USAGE_STATS["response_times"][key].append(response_time)

def get_api_statistics():
    """Get API usage statistics."""
    return API_USAGE_STATS

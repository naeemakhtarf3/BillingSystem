"""
Role-based access control for admission operations.

This module provides authentication and authorization functionality
for the patient admission and discharge workflow.
"""

from enum import Enum
from typing import List, Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
from app.core.config import settings

# Security scheme
security = HTTPBearer()

class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    RECEPTIONIST = "receptionist"
    BILLING = "billing"

class Permission(str, Enum):
    """Permission enumeration."""
    # Room permissions
    VIEW_ROOMS = "view_rooms"
    CREATE_ROOMS = "create_rooms"
    UPDATE_ROOMS = "update_rooms"
    DELETE_ROOMS = "delete_rooms"
    
    # Admission permissions
    VIEW_ADMISSIONS = "view_admissions"
    CREATE_ADMISSIONS = "create_admissions"
    UPDATE_ADMISSIONS = "update_admissions"
    DISCHARGE_PATIENTS = "discharge_patients"
    DELETE_ADMISSIONS = "delete_admissions"
    
    # Billing permissions
    VIEW_BILLING = "view_billing"
    CREATE_INVOICES = "create_invoices"
    UPDATE_INVOICES = "update_invoices"

# Role-based permissions mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.VIEW_ROOMS, Permission.CREATE_ROOMS, Permission.UPDATE_ROOMS, Permission.DELETE_ROOMS,
        Permission.VIEW_ADMISSIONS, Permission.CREATE_ADMISSIONS, Permission.UPDATE_ADMISSIONS, 
        Permission.DISCHARGE_PATIENTS, Permission.DELETE_ADMISSIONS,
        Permission.VIEW_BILLING, Permission.CREATE_INVOICES, Permission.UPDATE_INVOICES
    ],
    UserRole.DOCTOR: [
        Permission.VIEW_ROOMS, Permission.VIEW_ADMISSIONS, Permission.CREATE_ADMISSIONS, 
        Permission.UPDATE_ADMISSIONS, Permission.DISCHARGE_PATIENTS, Permission.VIEW_BILLING
    ],
    UserRole.NURSE: [
        Permission.VIEW_ROOMS, Permission.VIEW_ADMISSIONS, Permission.CREATE_ADMISSIONS, 
        Permission.UPDATE_ADMISSIONS, Permission.VIEW_BILLING
    ],
    UserRole.RECEPTIONIST: [
        Permission.VIEW_ROOMS, Permission.VIEW_ADMISSIONS, Permission.CREATE_ADMISSIONS, 
        Permission.VIEW_BILLING
    ],
    UserRole.BILLING: [
        Permission.VIEW_ROOMS, Permission.VIEW_ADMISSIONS, Permission.VIEW_BILLING, 
        Permission.CREATE_INVOICES, Permission.UPDATE_INVOICES
    ]
}

class User:
    """User model for authentication."""
    def __init__(self, user_id: str, username: str, role: UserRole, permissions: List[Permission]):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.permissions = permissions
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        return permission in self.permissions
    
    def has_any_permission(self, permissions: List[Permission]) -> bool:
        """Check if user has any of the specified permissions."""
        return any(permission in self.permissions for permission in permissions)
    
    def has_all_permissions(self, permissions: List[Permission]) -> bool:
        """Check if user has all of the specified permissions."""
        return all(permission in self.permissions for permission in permissions)

def create_access_token(user_id: str, username: str, role: UserRole) -> str:
    """Create JWT access token."""
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role.value,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = payload.get("user_id")
    username = payload.get("username")
    role_str = payload.get("role")
    
    if not all([user_id, username, role_str]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    try:
        role = UserRole(role_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user role"
        )
    
    permissions = ROLE_PERMISSIONS.get(role, [])
    return User(user_id, username, role, permissions)

def require_permission(permission: Permission):
    """Decorator to require specific permission."""
    def permission_checker(current_user: User = Depends(get_current_user)):
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission.value}"
            )
        return current_user
    return permission_checker

def require_any_permission(permissions: List[Permission]):
    """Decorator to require any of the specified permissions."""
    def permission_checker(current_user: User = Depends(get_current_user)):
        if not current_user.has_any_permission(permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of the following permissions required: {[p.value for p in permissions]}"
            )
        return current_user
    return permission_checker

def require_all_permissions(permissions: List[Permission]):
    """Decorator to require all of the specified permissions."""
    def permission_checker(current_user: User = Depends(get_current_user)):
        if not current_user.has_all_permissions(permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"All of the following permissions required: {[p.value for p in permissions]}"
            )
        return current_user
    return permission_checker

# Specific permission checkers for common operations
def require_room_access():
    """Require room viewing permission."""
    return require_permission(Permission.VIEW_ROOMS)

def require_admission_access():
    """Require admission viewing permission."""
    return require_permission(Permission.VIEW_ADMISSIONS)

def require_admission_creation():
    """Require admission creation permission."""
    return require_permission(Permission.CREATE_ADMISSIONS)

def require_discharge_permission():
    """Require patient discharge permission."""
    return require_permission(Permission.DISCHARGE_PATIENTS)

def require_billing_access():
    """Require billing access permission."""
    return require_permission(Permission.VIEW_BILLING)

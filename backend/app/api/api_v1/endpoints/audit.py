from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.audit_log import AuditLog, ActorType
from app.models.staff import Staff
from app.api.api_v1.endpoints.auth import get_current_staff
import uuid

router = APIRouter()

@router.get("/", response_model=List[dict])
def get_audit_logs(
    target_type: Optional[str] = Query(None),
    target_id: Optional[str] = Query(None),
    actor_id: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_staff: Staff = Depends(get_current_staff)
):
    """Get audit logs with optional filtering"""
    # Only admin can view audit logs
    if current_staff.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can view audit logs"
        )
    
    query = db.query(AuditLog)
    
    if target_type:
        query = query.filter(AuditLog.target_type == target_type)
    if target_id:
        # coerce string target_id to UUID for DB filter when possible
        try:
            tid = uuid.UUID(str(target_id))
            query = query.filter(AuditLog.target_id == tid)
        except Exception:
            # fallback: compare as string (for non-UUID ids)
            query = query.filter(AuditLog.target_id == target_id)
    if actor_id:
        query = query.filter(AuditLog.actor_id == actor_id)
    
    logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        {
            "id": str(log.id),
            "actor_type": log.actor_type,
            "actor_id": str(log.actor_id) if log.actor_id else None,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": str(log.target_id) if log.target_id else None,
            "details": log.details,
            "created_at": log.created_at
        }
        for log in logs
    ]

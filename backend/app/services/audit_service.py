from app.models.audit_log import AuditLog, ActorType
import uuid


def create_audit_log(db, actor_id=None, actor_type=None, action=None, target_type=None, target_id=None, details=None):
    """Create an audit log entry."""
    # Ensure actor_type is a valid ActorType value
    atype = None
    try:
        if actor_type:
            atype = ActorType(actor_type)
    except Exception:
        atype = ActorType.SYSTEM

    # Coerce actor_id and target_id to UUID objects when possible
    try:
        if actor_id and isinstance(actor_id, str):
            actor_id = uuid.UUID(actor_id)
    except Exception:
        # leave as-is if coercion fails
        pass

    try:
        if target_id and isinstance(target_id, str):
            target_id = uuid.UUID(target_id)
    except Exception:
        pass

    entry = AuditLog(
        actor_type=atype,
        actor_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog, ActorType
from typing import Optional, Dict, Any
import uuid

def log_audit_event(
    db: Session,
    action: str,
    actor_type: ActorType,
    actor_id: Optional[str] = None,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Log an audit event to the database"""
    audit_log = AuditLog(
        actor_type=actor_type,
        actor_id=uuid.UUID(actor_id) if actor_id else None,
        action=action,
        target_type=target_type,
        target_id=uuid.UUID(target_id) if target_id else None,
        details=details
    )
    
    db.add(audit_log)
    db.commit()
    return audit_log

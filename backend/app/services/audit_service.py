from typing import Optional, Dict, Any
import uuid
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog, ActorType


def log_audit_event(
    db: Session,
    action: str,
    actor_type: ActorType,
    actor_id: Optional[str] = None,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
):
    """Create and persist an audit event.

    actor_id and target_id may be UUID strings; non-UUID strings are stored as-is.
    """
    parsed_actor_id = None
    parsed_target_id = None
    try:
        parsed_actor_id = uuid.UUID(actor_id) if actor_id else None
    except Exception:
        parsed_actor_id = actor_id  # leave as-is if not UUID

    try:
        parsed_target_id = uuid.UUID(target_id) if target_id else None
    except Exception:
        parsed_target_id = target_id

    entry = AuditLog(
        actor_type=actor_type,
        actor_id=parsed_actor_id,
        action=action,
        target_type=target_type,
        target_id=parsed_target_id,
        details=details,
    )
    db.add(entry)
    db.commit()
    return entry


def log_report_access(
    db: Session,
    user_payload: Optional[Dict[str, Any]],
    report_name: str,
    action: str = "view_report",
    extra: Optional[Dict[str, Any]] = None,
):
    """Convenience hook for logging access to reports.

    - action: e.g., "view_report", "export_pdf"
    - report_name: e.g., "revenue", "patient_history", "outstanding"
    """
    actor_id = None
    actor_type = ActorType.SYSTEM
    if user_payload:
        actor_id = user_payload.get("sub") or user_payload.get("user_id")
        actor_type = ActorType.STAFF

    return log_audit_event(
        db=db,
        action=action,
        actor_type=actor_type,
        actor_id=actor_id,
        target_type="report",
        target_id=report_name,
        details=extra or {},
    )


# Backwards-compatible wrapper used by legacy endpoints
def create_audit_log(
    db,
    actor_id=None,
    actor_type=None,
    action=None,
    target_type=None,
    target_id=None,
    details=None,
):
    try:
        atype = ActorType(actor_type) if actor_type else ActorType.SYSTEM
    except Exception:
        atype = ActorType.SYSTEM
    return log_audit_event(
        db=db,
        action=action or "event",
        actor_type=atype,
        actor_id=actor_id,
        target_type=target_type,
        target_id=target_id,
        details=details,
    )

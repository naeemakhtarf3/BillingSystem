from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.services.report_service import ReportService
from app.core.security import require_roles
from app.db.session import get_db
from app.services.audit_service import log_report_access
from app.services.etl_service import ETLService


router = APIRouter(tags=["reports"])


def get_report_service() -> ReportService:
    return ReportService()


@router.get("/revenue")
def get_revenue(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    granularity: str = Query("month"),
    format: str = Query("json"),
    service: ReportService = Depends(get_report_service),
    db: Session = Depends(get_db),
):
    data = service.get_revenue_report(db, start_date=start_date, end_date=end_date, granularity=granularity)
    if format == "pdf":
        pdf = service.generate_revenue_pdf(db, start_date=start_date, end_date=end_date, granularity=granularity)
        return Response(content=pdf, media_type="application/pdf")
    return data


@router.get("/patients/{patient_id}/history")
def get_patient_history(
    patient_id: str,
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    status: str | None = Query(None),
    service: ReportService = Depends(get_report_service),
    db: Session = Depends(get_db),
):
    return service.get_patient_history(db, patient_id=patient_id, start_date=start_date, end_date=end_date, status=status)


@router.get("/outstanding")
def get_outstanding(
    min_days_overdue: int | None = Query(None, ge=0),
    max_days_overdue: int | None = Query(None, ge=0),
    min_amount: float | None = Query(None, ge=0),
    max_amount: float | None = Query(None, ge=0),
    format: str = Query("json"),
    service: ReportService = Depends(get_report_service),
    db: Session = Depends(get_db),
):
    data = service.get_outstanding_payments(
        db=db,
        min_days_overdue=min_days_overdue,
        max_days_overdue=max_days_overdue,
        min_amount=min_amount,
        max_amount=max_amount,
    )
    if format == "csv":
        csv_content = service.generate_outstanding_csv(db, min_days_overdue=min_days_overdue, max_days_overdue=max_days_overdue, min_amount=min_amount, max_amount=max_amount)
        return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=outstanding_payments.csv"})
    return data


@router.post("/etl/run")
def trigger_etl(
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
):
    """Manually trigger ETL process"""
    try:
        svc = ETLService()
        # naive parse; in practice validate
        f = from_date
        t = to_date
        if f or t:
            from datetime import datetime
            f = datetime.fromisoformat(f) if f else None
            t = datetime.fromisoformat(t) if t else None
        svc.run_for_range(from_date=f, to_date=t)
        return {"status": "ok", "message": "ETL process completed successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/etl/setup")
def setup_production_data():
    """Setup production data - run migrations and ETL"""
    try:
        import subprocess
        import os
        
        # Change to backend directory
        backend_dir = os.path.join(os.getcwd(), 'backend')
        if not os.path.exists(backend_dir):
            backend_dir = os.getcwd()
        
        # Run migrations
        result = subprocess.run(
            ["alembic", "upgrade", "head"], 
            cwd=backend_dir, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            return {"status": "error", "message": f"Migration failed: {result.stderr}"}
        
        # Run ETL
        svc = ETLService()
        svc.run_for_range(None, None)
        
        return {
            "status": "ok", 
            "message": "Production setup completed successfully",
            "migration_output": result.stdout
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}



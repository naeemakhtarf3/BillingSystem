from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, patients, invoices, payments, audit, reports, rooms, admissions

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(admissions.router, prefix="/admissions", tags=["admissions"])

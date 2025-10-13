from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, patients, invoices, payments, audit

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
import logging
import os
from app.api.api_v1.api import api_router
from app.db.session import Base, engine
from app.agents.simple_clinic_agent import agent_app
from app.services.etl_service import ETLService

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Clinic Billing System API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Log resolved DATABASE_URL on startup for easier debugging of relative paths
logging.getLogger("uvicorn.error").info(f"Resolved DATABASE_URL: {settings.DATABASE_URL}")

# Set up CORS
# Allow all origins temporarily to fix CORS issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router FIRST (before static files)
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount agent application for AI communication
app.mount("/agent", agent_app)

@app.on_event("startup")
async def startup_event():
    """Initialize ETL data on startup"""
    try:
        logging.getLogger("uvicorn.error").info("Running initial ETL process...")
        etl_service = ETLService()
        etl_service.run_for_range(None, None)
        logging.getLogger("uvicorn.error").info("ETL process completed successfully")
    except Exception as e:
        logging.getLogger("uvicorn.error").error(f"ETL process failed: {e}")
        # Don't fail startup if ETL fails



@app.get("/")
async def root():
    return {"message": "Clinic Billing System API", "version": settings.APP_VERSION}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

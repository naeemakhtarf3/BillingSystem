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
        logger = logging.getLogger("uvicorn.error")
        logger.info("Starting application initialization...")
        logger.info(f"Database URL: {settings.DATABASE_URL}")
        
        # Check if we're in production
        if settings.ENVIRONMENT != "local":
            logger.info("Production environment detected - running ETL process...")
            etl_service = ETLService()
            etl_service.run_for_range(None, None)
            logger.info("ETL process completed successfully")
        else:
            logger.info("Local environment - skipping ETL process")
            
    except Exception as e:
        logger = logging.getLogger("uvicorn.error")
        logger.error(f"Startup process failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Don't fail startup if ETL fails



@app.get("/")
async def root():
    return {"message": "Clinic Billing System API", "version": settings.APP_VERSION}

@app.get("/health")
async def health_check():
    """Health check endpoint that verifies database tables exist"""
    try:
        from sqlalchemy import text
        from app.db.session import engine
        from app.core.config import settings
        
        # Check if reporting tables exist
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('revenue_metrics', 'patient_payment_history', 'outstanding_payments', 'etl_process_status')
            """))
            tables = [row[0] for row in result.fetchall()]
            
            # Get row counts for each table
            table_counts = {}
            for table in tables:
                try:
                    count_result = conn.execute(text(f'SELECT COUNT(*) FROM {table}'))
                    table_counts[table] = count_result.fetchone()[0]
                except Exception as e:
                    table_counts[table] = f"Error: {str(e)}"
            
            if len(tables) == 4:
                return {
                    "status": "healthy",
                    "database": "connected",
                    "database_url": settings.DATABASE_URL[:50] + "..." if len(settings.DATABASE_URL) > 50 else settings.DATABASE_URL,
                    "reporting_tables": "all_present",
                    "tables": tables,
                    "table_counts": table_counts
                }
            else:
                return {
                    "status": "degraded",
                    "database": "connected",
                    "database_url": settings.DATABASE_URL[:50] + "..." if len(settings.DATABASE_URL) > 50 else settings.DATABASE_URL,
                    "reporting_tables": "missing",
                    "expected": 4,
                    "found": len(tables),
                    "tables": tables,
                    "table_counts": table_counts
                }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "database_url": settings.DATABASE_URL[:50] + "..." if len(settings.DATABASE_URL) > 50 else settings.DATABASE_URL,
            "error": str(e)
        }

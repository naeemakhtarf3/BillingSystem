from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import logging
from app.api.api_v1.api import api_router
from app.db.session import Base, engine
from app.agents.simple_clinic_agent import agent_app

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
# Allow any localhost origin (any port) in development via regex, while keeping
# the explicit list in settings as fallback. This accepts http(s)://localhost(:port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount agent application for AI communication
app.mount("/agent", agent_app)

@app.get("/")
async def root():
    return {"message": "Clinic Billing System API", "version": settings.APP_VERSION}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

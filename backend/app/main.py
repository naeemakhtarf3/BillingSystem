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

# Mount static files from static directory (copied during build)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    # Mount static files at root, but API routes take precedence due to order
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    # Catch-all route for SPA routing (must be last)
    @app.get("/{path:path}")
    async def serve_spa(path: str):
        # Skip API routes and agent routes
        if path.startswith("api/") or path.startswith("agent/"):
            return {"error": "Not found"}
        # Serve index.html for all other routes to support client-side routing
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"error": "Not found"}

@app.get("/")
async def root():
    return {"message": "Clinic Billing System API", "version": settings.APP_VERSION}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

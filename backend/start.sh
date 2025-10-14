#!/bin/bash
# Startup script for Render.com deployment

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Create sample data if needed (only for first deployment)
echo "Checking if sample data exists..."
python -c "
from app.db.session import SessionLocal
from app.models.staff import Staff
from sqlalchemy.orm import Session

db = SessionLocal()
try:
    admin_exists = db.query(Staff).filter(Staff.email == 'admin@clinic.com').first()
    if not admin_exists:
        print('Creating sample data...')
        exec(open('create_sample_data.py').read())
    else:
        print('Sample data already exists')
finally:
    db.close()
"

# Start the application
echo "Starting FastAPI application..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT

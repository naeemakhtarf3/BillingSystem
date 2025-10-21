#!/usr/bin/env python3
"""
Production deployment setup script
This script ensures database migrations and ETL processes run correctly
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description, required=True):
    """Run a command and return the result"""
    logger.info(f"Running: {description}")
    logger.info(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            logger.info(f"Output: {result.stdout}")
        logger.info(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed")
        if e.stderr:
            logger.error(f"Error: {e.stderr}")
        if required:
            logger.error("This is a required step - deployment will fail")
            return False
        else:
            logger.warning("This is an optional step - continuing deployment")
            return True

def check_database_connection():
    """Check if database connection is working"""
    try:
        from app.core.config import settings
        from app.db.session import engine
        
        logger.info(f"Testing database connection to: {settings.DATABASE_URL}")
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main deployment setup function"""
    logger.info("🚀 Starting production deployment setup")
    logger.info("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("alembic.ini"):
        logger.error("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    # Check database connection
    if not check_database_connection():
        logger.error("❌ Database connection failed - aborting deployment")
        sys.exit(1)
    
    # Run setup commands
    setup_commands = [
        ("alembic upgrade head", "Running database migrations", True),
        ("python create_sample_data.py", "Creating sample data", False),  # Optional
        ("python etl.py", "Running ETL process", False),  # Optional
    ]
    
    success_count = 0
    total_count = len(setup_commands)
    
    for command, description, required in setup_commands:
        if run_command(command, description, required):
            success_count += 1
        else:
            if required:
                logger.error(f"❌ Deployment setup failed at: {description}")
                sys.exit(1)
            else:
                logger.warning(f"⚠️ Optional step failed: {description}")
    
    logger.info("=" * 50)
    logger.info(f"🎉 Deployment setup completed! ({success_count}/{total_count} steps successful)")
    
    # Final database check
    try:
        from app.db.session import engine
        with engine.connect() as conn:
            # Check if reporting tables exist
            result = conn.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('revenue_metrics', 'patient_payment_history', 'outstanding_payments', 'etl_process_status')
            """)
            tables = [row[0] for row in result.fetchall()]
            
            if len(tables) == 4:
                logger.info("✅ All reporting tables created successfully")
            else:
                logger.warning(f"⚠️ Only {len(tables)}/4 reporting tables found: {tables}")
                
    except Exception as e:
        logger.error(f"❌ Final database check failed: {e}")

if __name__ == "__main__":
    main()

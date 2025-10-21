#!/usr/bin/env python3
"""
Production setup script for Render deployment
This script handles database setup and ETL initialization
"""

import os
import sys
import subprocess
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and return the result"""
    logger.info(f"Running: {description}")
    logger.info(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            logger.info(f"Output: {result.stdout}")
        if result.stderr:
            logger.warning(f"Stderr: {result.stderr}")
        logger.info(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed")
        if e.stderr:
            logger.error(f"Error: {e.stderr}")
        return False

def main():
    """Main production setup function"""
    logger.info("🚀 Starting production setup")
    logger.info("=" * 50)
    
    # Change to backend directory
    os.chdir('backend')
    logger.info(f"Changed to directory: {os.getcwd()}")
    
    # Step 1: Run database migrations
    if not run_command("alembic upgrade head", "Running database migrations"):
        logger.error("❌ Database migrations failed - aborting")
        sys.exit(1)
    
    # Step 2: Create sample data (optional)
    logger.info("Creating sample data...")
    run_command("python create_sample_data.py", "Creating sample data")
    
    # Step 3: Run ETL process
    logger.info("Running ETL process...")
    if not run_command("python etl.py", "Running ETL process"):
        logger.warning("⚠️ ETL process failed - continuing anyway")
    
    # Step 4: Verify tables exist
    logger.info("Verifying database setup...")
    try:
        sys.path.insert(0, os.getcwd())
        from app.db.session import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Check if reporting tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('revenue_metrics', 'patient_payment_history', 'outstanding_payments', 'etl_process_status')
            """))
            tables = [row[0] for row in result.fetchall()]
            
            logger.info(f"Found {len(tables)}/4 reporting tables: {tables}")
            
            if len(tables) == 4:
                logger.info("✅ All reporting tables created successfully")
            else:
                logger.warning(f"⚠️ Missing tables: {set(['revenue_metrics', 'patient_payment_history', 'outstanding_payments', 'etl_process_status']) - set(tables)}")
                
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    logger.info("🎉 Production setup completed!")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Direct production database setup script
This script directly connects to the production database and sets up tables
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_production_database():
    """Setup production database directly"""
    try:
        # Set production database URL
        os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_Xzxog43QnSfN@ep-lively-lab-admvsm99-pooler.c-2.us-east-1.aws.neon.tech/billingdb1?sslmode=require&channel_binding=require'
        os.environ['ENVIRONMENT'] = 'production'
        
        # Add current directory to Python path
        sys.path.insert(0, os.getcwd())
        
        from app.core.config import settings
        from app.db.session import engine
        from app.services.etl_service import ETLService
        from sqlalchemy import text
        
        logger.info(f"Connecting to database: {settings.DATABASE_URL}")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
        
        # Run migrations
        logger.info("Running Alembic migrations...")
        import subprocess
        result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"❌ Migration failed: {result.stderr}")
            return False
        
        logger.info("✅ Migrations completed successfully")
        
        # Create sample data
        logger.info("Creating sample data...")
        result = subprocess.run(["python", "create_sample_data.py"], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.warning(f"⚠️ Sample data creation failed: {result.stderr}")
        else:
            logger.info("✅ Sample data created successfully")
        
        # Run ETL process
        logger.info("Running ETL process...")
        etl_service = ETLService()
        etl_service.run_for_range(None, None)
        logger.info("✅ ETL process completed successfully")
        
        # Verify tables
        logger.info("Verifying tables...")
        with engine.connect() as conn:
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
                
                # Check data in each table
                for table in tables:
                    count_result = conn.execute(text(f'SELECT COUNT(*) FROM {table}'))
                    count = count_result.fetchone()[0]
                    logger.info(f"  {table}: {count} rows")
                
                return True
            else:
                missing = set(['revenue_metrics', 'patient_payment_history', 'outstanding_payments', 'etl_process_status']) - set(tables)
                logger.error(f"❌ Missing tables: {missing}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main function"""
    logger.info("🚀 Setting up production database directly...")
    logger.info("=" * 50)
    
    if setup_production_database():
        logger.info("🎉 Production database setup completed successfully!")
        logger.info("You can now check the health endpoint:")
        logger.info("curl https://billingapi-ntlg.onrender.com/health")
    else:
        logger.error("❌ Production database setup failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

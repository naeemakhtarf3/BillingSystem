#!/usr/bin/env python3
"""
Test script to verify production database connection and tables
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection and check tables"""
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.getcwd())
        
        from app.core.config import settings
        from app.db.session import engine
        from sqlalchemy import text
        
        logger.info(f"Testing database connection to: {settings.DATABASE_URL}")
        
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            
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
                logger.info("✅ All reporting tables exist")
                
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
        logger.error(f"❌ Database test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main test function"""
    logger.info("🧪 Testing production database...")
    logger.info("=" * 50)
    
    if test_database_connection():
        logger.info("🎉 Database test passed!")
        return 0
    else:
        logger.error("❌ Database test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())

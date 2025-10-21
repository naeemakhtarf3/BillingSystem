#!/usr/bin/env python3
"""
Manually create reporting tables using direct SQL
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_reporting_tables():
    """Create reporting tables manually"""
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.getcwd())
        
        from app.core.config import settings
        from app.db.session import engine
        from sqlalchemy import text
        
        logger.info(f"Connecting to database: {settings.DATABASE_URL}")
        
        with engine.connect() as conn:
            # Create revenue_metrics table
            logger.info("Creating revenue_metrics table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS revenue_metrics (
                    id SERIAL PRIMARY KEY,
                    date_key DATE NOT NULL,
                    total_revenue NUMERIC(10, 2) NOT NULL DEFAULT 0,
                    payment_count INTEGER NOT NULL DEFAULT 0,
                    average_payment NUMERIC(10, 2) NOT NULL DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            
            # Create index on date_key
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_revenue_metrics_date_key ON revenue_metrics(date_key)"))
            
            # Create patient_payment_history table
            logger.info("Creating patient_payment_history table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS patient_payment_history (
                    id SERIAL PRIMARY KEY,
                    patient_id VARCHAR(50) NOT NULL,
                    payment_date DATE NOT NULL,
                    amount NUMERIC(10, 2) NOT NULL,
                    payment_status VARCHAR(20) NOT NULL,
                    invoice_id VARCHAR(50),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            
            # Create indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_patient_payment_history_patient_id ON patient_payment_history(patient_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_patient_payment_history_payment_date ON patient_payment_history(payment_date)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_patient_payment_history_status ON patient_payment_history(payment_status)"))
            
            # Create outstanding_payments table
            logger.info("Creating outstanding_payments table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS outstanding_payments (
                    id SERIAL PRIMARY KEY,
                    patient_id VARCHAR(50) NOT NULL,
                    invoice_id VARCHAR(50) NOT NULL,
                    amount_due NUMERIC(10, 2) NOT NULL,
                    days_overdue INTEGER NOT NULL,
                    last_payment_date DATE,
                    payment_status VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            
            # Create indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_outstanding_payments_patient_id ON outstanding_payments(patient_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_outstanding_payments_days_overdue ON outstanding_payments(days_overdue)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_outstanding_payments_status ON outstanding_payments(payment_status)"))
            
            # Create etl_process_status table
            logger.info("Creating etl_process_status table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS etl_process_status (
                    id SERIAL PRIMARY KEY,
                    process_name VARCHAR(100) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    completed_at TIMESTAMP WITH TIME ZONE,
                    records_processed INTEGER DEFAULT 0,
                    error_message TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            
            # Commit the transaction
            conn.commit()
            logger.info("✅ All reporting tables created successfully!")
            
            # Verify tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('revenue_metrics', 'patient_payment_history', 'outstanding_payments', 'etl_process_status')
            """))
            tables = [row[0] for row in result.fetchall()]
            
            logger.info(f"Found {len(tables)}/4 reporting tables: {tables}")
            
            if len(tables) == 4:
                logger.info("✅ All reporting tables verified!")
                return True
            else:
                missing = set(['revenue_metrics', 'patient_payment_history', 'outstanding_payments', 'etl_process_status']) - set(tables)
                logger.error(f"❌ Missing tables: {missing}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Failed to create reporting tables: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main function"""
    logger.info("🚀 Creating reporting tables manually...")
    logger.info("=" * 50)
    
    if create_reporting_tables():
        logger.info("🎉 Reporting tables created successfully!")
        logger.info("Now you can run the ETL process to populate them with data.")
        return 0
    else:
        logger.error("❌ Failed to create reporting tables!")
        return 1

if __name__ == "__main__":
    sys.exit(main())

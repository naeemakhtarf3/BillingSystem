import os
import sys
from sqlalchemy import create_engine, text
from app.core.config import settings

# Use the proper database URL from configuration
engine = create_engine(settings.DATABASE_URL)
print(f"Using database URL: {settings.DATABASE_URL}")

with engine.connect() as conn:
    # Check if it's SQLite or PostgreSQL
    if 'sqlite' in settings.DATABASE_URL:
        result = conn.execute(text('SELECT name FROM sqlite_master WHERE type="table"'))
    else:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
    
    tables = [row[0] for row in result]
    print("Tables in database:", tables)
    
    if 'revenue_metrics' in tables:
        print("revenue_metrics table exists")
        count_result = conn.execute(text('SELECT COUNT(*) FROM revenue_metrics'))
        count = count_result.fetchone()[0]
        print(f"Rows in revenue_metrics: {count}")
    else:
        print("revenue_metrics table does not exist")

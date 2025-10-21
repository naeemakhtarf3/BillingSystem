import os
from sqlalchemy import create_engine, text
engine = create_engine('sqlite:///clinic_billing.db')
with engine.connect() as conn:
    result = conn.execute(text('SELECT name FROM sqlite_master WHERE type="table"'))
    tables = [row[0] for row in result]
    print("Tables in database:", tables)
    if 'revenue_metrics' in tables:
        print("revenue_metrics table exists")
        count_result = conn.execute(text('SELECT COUNT(*) FROM revenue_metrics'))
        count = count_result.fetchone()[0]
        print(f"Rows in revenue_metrics: {count}")
    else:
        print("revenue_metrics table does not exist")

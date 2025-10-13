from sqlalchemy import create_engine, text
from app.core.config import settings

print('Using DATABASE_URL:', settings.DATABASE_URL)
engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    try:
        res = conn.execute(text('SELECT id, email, password_hash FROM staff'))
        rows = res.fetchall()
        print('Found', len(rows), 'staff rows')
        for r in rows:
            print(r)
    except Exception as e:
        print('Error querying staff table:', e)

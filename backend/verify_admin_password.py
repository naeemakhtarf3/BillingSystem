from app.core.config import settings
from sqlalchemy import create_engine, text
from app.core.security import verify_password

print('Using DATABASE_URL:', settings.DATABASE_URL)
engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    res = conn.execute(text("SELECT email, password_hash FROM staff WHERE email='admin@clinic.com'"))
    row = res.fetchone()
    if not row:
        print('Admin user not found')
    else:
        email, hashed = row
        print('Found admin:', email)
        print('verify_password("admin123", hash) ->', verify_password('admin123', hashed))

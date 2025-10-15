#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def test_database_connection():
    try:
        print(f"Testing database connection to: postgresql://neondb_owner:npg_Xzxog43QnSfN@ep-lively-lab-admvsm99-pooler.c-2.us-east-1.aws.neon.tech/billingdb1?sslmode=require&channel_binding=require")
        engine = create_engine("postgresql://neondb_owner:npg_Xzxog43QnSfN@ep-lively-lab-admvsm99-pooler.c-2.us-east-1.aws.neon.tech/billingdb1?sslmode=require&channel_binding=require")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
    except SQLAlchemyError as e:
        print(f"❌ Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()

#!/usr/bin/env python3
"""
Production Database Migration Script

This script runs database migrations for the production environment.
It sets the environment to production and runs alembic migrations.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Set environment to production
    os.environ["ENVIRONMENT"] = "production"
    
    # Add the backend directory to Python path
    backend_dir = Path(__file__).parent
    sys.path.insert(0, str(backend_dir))
    
    try:
        # Import settings to verify configuration
        from app.core.config import settings
        print(f"Environment: {settings.ENVIRONMENT}")
        print(f"Database URL: {settings.DATABASE_URL[:50]}...")
        
        # Run alembic upgrade
        print("\nRunning database migrations...")
        result = subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], cwd=backend_dir, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database migrations completed successfully!")
            print(result.stdout)
        else:
            print("❌ Database migration failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

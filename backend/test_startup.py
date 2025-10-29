#!/usr/bin/env python3
"""
Test script to debug startup issues
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_imports():
    """Test all imports step by step"""
    print("Testing imports...")
    
    try:
        print("1. Testing basic imports...")
        import logging
        print("   ✓ logging imported")
        
        print("2. Testing FastAPI...")
        from fastapi import FastAPI
        print("   ✓ FastAPI imported")
        
        print("3. Testing config...")
        from app.core.config import settings
        print(f"   ✓ Config imported - Environment: {settings.ENVIRONMENT}")
        print(f"   ✓ Database URL: {settings.DATABASE_URL[:50]}...")
        
        print("4. Testing database session...")
        from app.db.session import Base, engine
        print("   ✓ Database session imported")
        
        print("5. Testing models...")
        from app.models import *
        print("   ✓ Models imported")
        
        print("6. Testing API router...")
        from app.api.api_v1.api import api_router
        print("   ✓ API router imported")
        
        print("7. Testing agent...")
        from app.agents.simple_clinic_agent import agent_app
        print("   ✓ Agent app imported")
        
        print("8. Testing ETL service...")
        from app.services.etl_service import ETLService
        print("   ✓ ETL service imported")
        
        print("9. Testing websocket...")
        from app.core.websocket import websocket_endpoint
        print("   ✓ Websocket imported")
        
        print("10. Testing exceptions...")
        from app.core.exceptions import setup_exception_handlers
        print("   ✓ Exception handlers imported")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        from app.db.session import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("   ✓ Database connection successful!")
            return True
            
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False

def test_app_creation():
    """Test FastAPI app creation"""
    print("\nTesting FastAPI app creation...")
    
    try:
        from app.main import app
        print("   ✓ FastAPI app created successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ FastAPI app creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Debugging Backend Startup Issues")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed - check dependencies")
        sys.exit(1)
    
    # Test database
    if not test_database_connection():
        print("\n❌ Database test failed - check database configuration")
        sys.exit(1)
    
    # Test app creation
    if not test_app_creation():
        print("\n❌ App creation test failed - check main.py")
        sys.exit(1)
    
    print("\n🎉 All tests passed! Backend should start successfully.")

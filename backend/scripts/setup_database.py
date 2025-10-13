#!/usr/bin/env python3
"""
Database setup script for Clinic Billing System
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and return the result"""
    print(f"\n🗄️  {description}")
    print(f"Running: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("Please copy env.example to .env and configure your database settings")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
        if "postgresql://" not in content:
            print("❌ DATABASE_URL not configured in .env file")
            return False
        if "your-super-secret-jwt-key" in content:
            print("⚠️  Please change the JWT_SECRET_KEY in .env file")
            return False
    
    print("✅ .env file configuration looks good")
    return True

def main():
    """Main database setup function"""
    print("🏥 Clinic Billing System - Database Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("alembic.ini"):
        print("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    # Check environment configuration
    if not check_env_file():
        print("\nPlease configure your .env file and run this script again")
        sys.exit(1)
    
    # Database setup commands
    setup_commands = [
        ("alembic upgrade head", "Running database migrations"),
        ("python create_sample_data.py", "Creating sample data"),
    ]
    
    success_count = 0
    total_count = len(setup_commands)
    
    for command, description in setup_commands:
        if run_command(command, description):
            success_count += 1
        else:
            print(f"\n❌ Database setup failed at: {description}")
            print("Please check your database connection and try again")
            break
    
    print("\n" + "=" * 50)
    if success_count == total_count:
        print("🎉 Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Start the backend server: uvicorn app.main:app --reload")
        print("2. Access the API docs at: http://localhost:8000/docs")
        print("3. Login with admin@clinic.com / admin123")
        return 0
    else:
        print("⚠️  Database setup incomplete. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Setup script for Clinic Billing System
This script helps set up the development environment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a shell command and return the result"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return e

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check Node.js
    try:
        result = run_command("node --version", check=False)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()}")
        else:
            print("❌ Node.js is not installed")
            return False
    except:
        print("❌ Node.js is not installed")
        return False
    
    # Check npm
    try:
        result = run_command("npm --version", check=False)
        if result.returncode == 0:
            print(f"✅ npm {result.stdout.strip()}")
        else:
            print("❌ npm is not installed")
            return False
    except:
        print("❌ npm is not installed")
        return False
    
    # Check PostgreSQL
    try:
        result = run_command("psql --version", check=False)
        if result.returncode == 0:
            print(f"✅ PostgreSQL {result.stdout.strip()}")
        else:
            print("❌ PostgreSQL is not installed")
            return False
    except:
        print("❌ PostgreSQL is not installed")
        return False
    
    return True

def setup_backend():
    """Set up the backend environment"""
    print("\n🚀 Setting up backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Create virtual environment
    venv_dir = backend_dir / "venv"
    if not venv_dir.exists():
        print("Creating virtual environment...")
        run_command(f"python -m venv {venv_dir}")
    
    # Determine activation script based on OS
    if os.name == 'nt':  # Windows
        activate_script = venv_dir / "Scripts" / "activate.bat"
        pip_cmd = str(venv_dir / "Scripts" / "pip")
    else:  # Unix/Linux/MacOS
        activate_script = venv_dir / "bin" / "activate"
        pip_cmd = str(venv_dir / "bin" / "pip")
    
    # Install dependencies
    print("Installing Python dependencies...")
    run_command(f"{pip_cmd} install -r requirements.txt", cwd=backend_dir)
    
    # Create .env file if it doesn't exist
    env_file = backend_dir / ".env"
    env_example = backend_dir / "env.example"
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from template...")
        shutil.copy(env_example, env_file)
        print("⚠️  Please edit backend/.env with your database and Stripe credentials")
    
    return True

def setup_frontend():
    """Set up the frontend environment"""
    print("\n🎨 Setting up frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install dependencies
    print("Installing Node.js dependencies...")
    run_command("npm install", cwd=frontend_dir)
    
    return True

def setup_database():
    """Set up the database"""
    print("\n🗄️  Setting up database...")
    
    print("Please ensure PostgreSQL is running and create a database:")
    print("1. Connect to PostgreSQL as superuser")
    print("2. Run: CREATE DATABASE clinic_billing;")
    print("3. Run: CREATE USER clinic_user WITH PASSWORD 'your_password';")
    print("4. Run: GRANT ALL PRIVILEGES ON DATABASE clinic_billing TO clinic_user;")
    print("5. Update the DATABASE_URL in backend/.env")
    
    # Check if .env exists and has database URL
    env_file = Path("backend/.env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if "postgresql://" in content and "clinic_billing" in content:
                print("✅ Database URL found in .env")
                return True
    
    print("⚠️  Please configure DATABASE_URL in backend/.env")
    return False

def main():
    """Main setup function"""
    print("🏥 Clinic Billing System Setup")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please install missing tools.")
        return False
    
    # Setup backend
    if not setup_backend():
        print("\n❌ Backend setup failed.")
        return False
    
    # Setup frontend
    if not setup_frontend():
        print("\n❌ Frontend setup failed.")
        return False
    
    # Setup database
    setup_database()
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Configure backend/.env with your database and Stripe credentials")
    print("2. Run database migrations: cd backend && alembic upgrade head")
    print("3. Create sample data: cd backend && python create_sample_data.py")
    print("4. Start backend: cd backend && uvicorn app.main:app --reload")
    print("5. Start frontend: cd frontend && npm run dev")
    print("\nAccess the application:")
    print("- Frontend: http://localhost:5173")
    print("- Backend API: http://localhost:8000")
    print("- API Docs: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

@echo off
echo 🏥 Clinic Billing System Setup
echo ================================

echo.
echo 🔍 Checking requirements...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)
echo ✅ Python is installed

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    pause
    exit /b 1
)
echo ✅ Node.js is installed

REM Check npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed or not in PATH
    pause
    exit /b 1
)
echo ✅ npm is installed

echo.
echo 🚀 Setting up backend...

REM Create virtual environment
if not exist "backend\venv" (
    echo Creating virtual environment...
    python -m venv backend\venv
)

REM Install Python dependencies
echo Installing Python dependencies...
call backend\venv\Scripts\activate.bat
pip install -r backend\requirements.txt

REM Create .env file if it doesn't exist
if not exist "backend\.env" (
    if exist "backend\env.example" (
        echo Creating .env file from template...
        copy "backend\env.example" "backend\.env"
        echo ⚠️  Please edit backend\.env with your database and Stripe credentials
    )
)

echo.
echo 🎨 Setting up frontend...

REM Install Node.js dependencies
echo Installing Node.js dependencies...
cd frontend
npm install
cd ..

echo.
echo 🗄️  Database Setup Required
echo Please ensure PostgreSQL is running and create a database:
echo 1. Connect to PostgreSQL as superuser
echo 2. Run: CREATE DATABASE clinic_billing;
echo 3. Run: CREATE USER clinic_user WITH PASSWORD 'your_password';
echo 4. Run: GRANT ALL PRIVILEGES ON DATABASE clinic_billing TO clinic_user;
echo 5. Update the DATABASE_URL in backend\.env

echo.
echo 🎉 Setup completed!
echo.
echo Next steps:
echo 1. Configure backend\.env with your database and Stripe credentials
echo 2. Run database migrations: cd backend ^&^& alembic upgrade head
echo 3. Create sample data: cd backend ^&^& python create_sample_data.py
echo 4. Start backend: cd backend ^&^& uvicorn app.main:app --reload
echo 5. Start frontend: cd frontend ^&^& npm run dev
echo.
echo Access the application:
echo - Frontend: http://localhost:5173
echo - Backend API: http://localhost:8000
echo - API Docs: http://localhost:8000/docs

pause

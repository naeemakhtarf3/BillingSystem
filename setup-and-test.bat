@echo off
echo ========================================
echo Clinic Billing System - Test Setup
echo ========================================
echo.

echo Step 1: Checking frontend dependencies...
cd frontend
if not exist node_modules (
    echo Installing frontend dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install frontend dependencies
        pause
        exit /b 1
    )
) else (
    echo Frontend dependencies already installed
)
cd ..

echo.
echo Step 2: Checking backend dependencies...
cd backend
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)
cd ..

echo.
echo Step 3: Starting servers...
echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && call venv\Scripts\activate && python -m uvicorn app.main:app --reload --port 8000"

echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak >nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo Waiting 10 seconds for frontend to start...
timeout /t 10 /nobreak >nul

echo.
echo Step 4: Verifying servers are running...
echo Checking backend...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Backend server may not be running properly
) else (
    echo ✓ Backend server is running
)

echo Checking frontend...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Frontend server may not be running properly
) else (
    echo ✓ Frontend server is running
)

echo.
echo Step 5: Running Playwright tests...
echo.
npx playwright test seed.spec.ts --reporter=html

echo.
echo ========================================
echo Test run completed!
echo ========================================
echo.
echo To view the HTML report, run: npx playwright show-report
echo.
pause

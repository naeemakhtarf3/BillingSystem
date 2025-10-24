@echo off
echo Starting Playwright Tests for Clinic Billing System
echo.

echo Checking if backend is running...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Backend server not detected at http://localhost:8000
    echo Please start the backend server first:
    echo   cd backend
    echo   python -m uvicorn app.main:app --reload --port 8000
    echo.
)

echo Checking if frontend is running...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Frontend server not detected at http://localhost:3000
    echo Please start the frontend server first:
    echo   cd frontend
    echo   npm run dev
    echo.
)

echo Running Playwright tests...
echo.

REM Use manual mode by default (more reliable)
echo Running tests in manual mode (servers should be running)...
npx playwright test seed.spec.ts --config=playwright.config.manual.ts --reporter=html

echo.
echo Test run completed!
echo To view the HTML report, run: npx playwright show-report
echo.
pause

@echo off
echo ========================================
echo Comprehensive Patient Page Test Runner
echo ========================================
echo.

echo Step 1: Checking server status...
echo.

echo Checking Frontend (port 5173)...
curl -s http://localhost:5173 >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Frontend server not running on port 5173
    echo Please start frontend: cd frontend ^&^& npm run dev
    echo.
) else (
    echo ✅ Frontend server is running on port 5173
)

echo Checking Backend (port 8000)...
curl -s http://localhost:8000/docs >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Backend server not running on port 8000
    echo Please start backend: cd backend ^&^& .\venv\Scripts\activate ^&^& python -m uvicorn app.main:app --reload --port 8000
    echo.
) else (
    echo ✅ Backend server is running on port 8000
)

echo.
echo Step 2: Running comprehensive tests...
echo.

REM Run tests with just Chrome for better reliability
npx playwright test seed.spec.ts --config=playwright.config.manual.ts --project=chromium --headed --reporter=html

echo.
echo ========================================
echo Test Results Summary
echo ========================================
echo.
echo To view detailed HTML report: npx playwright show-report
echo.
pause

@echo off
echo Starting Clinic Billing System Servers
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"

echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are starting in separate windows.
echo Wait for both to be ready before running tests.
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
pause

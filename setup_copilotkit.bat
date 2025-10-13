@echo off
echo Setting up ADK + AG-UI + CopilotKit integration for Clinic Billing System...
echo.

echo Installing backend dependencies...
cd backend
pip install -r requirements.txt
echo.

echo Installing frontend dependencies...
cd ..\frontend
npm install
echo.

echo Setup complete! 
echo.
echo To start the system:
echo 1. Start the backend: cd backend && uvicorn app.main:app --reload --port 8000
echo 2. Start the frontend: cd frontend && npm run dev
echo.
echo The AI assistant will be available at http://localhost:5173
echo The AG-UI endpoint will be at http://localhost:8000/ag-ui
echo.
pause

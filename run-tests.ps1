Write-Host "Starting Playwright Tests for Clinic Billing System" -ForegroundColor Green
Write-Host ""

Write-Host "Checking if backend is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓ Backend server is running" -ForegroundColor Green
} catch {
    Write-Host "⚠ WARNING: Backend server not detected at http://localhost:8000" -ForegroundColor Red
    Write-Host "Please start the backend server first:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor Cyan
    Write-Host "  python -m uvicorn app.main:app --reload --port 8000" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "Checking if frontend is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓ Frontend server is running" -ForegroundColor Green
} catch {
    Write-Host "⚠ WARNING: Frontend server not detected at http://localhost:3000" -ForegroundColor Red
    Write-Host "Please start the frontend server first:" -ForegroundColor Yellow
    Write-Host "  cd frontend" -ForegroundColor Cyan
    Write-Host "  npm run dev" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "Running Playwright tests..." -ForegroundColor Green
Write-Host ""

# Run the tests
npx playwright test seed.spec.ts --reporter=html

Write-Host ""
Write-Host "Test run completed!" -ForegroundColor Green
Write-Host "To view the HTML report, run: npx playwright show-report" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to continue"

@echo off
echo Running Playwright Tests (Manual Mode)
echo.

echo Make sure both servers are running:
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:3000
echo.

echo If servers are not running, use: start-servers.bat
echo.

pause

echo Running tests...
npx playwright test seed.spec.ts --config=playwright.config.manual.ts --reporter=html

echo.
echo Test completed!
echo To view report: npx playwright show-report
pause

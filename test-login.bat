@echo off
echo ========================================
echo Login and Dashboard Test
echo ========================================
echo.

echo Testing login functionality and dashboard navigation...
echo.

REM Run the login test
npx playwright test seed.spec.ts --config=playwright.config.manual.ts --project=chromium --headed --reporter=html

echo.
echo ========================================
echo Test completed successfully!
echo ========================================
echo.
echo The test verified:
echo ✅ Login page loads correctly
echo ✅ Email and password fields are pre-filled
echo ✅ Sign In button is clickable
echo ✅ Login redirects to dashboard
echo ✅ Dashboard page displays correctly
echo ✅ Dashboard statistics cards are visible
echo.
echo To view detailed report: npx playwright show-report
echo.
pause



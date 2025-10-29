@echo off
echo Starting Production Deployment...
echo ========================================

REM Set environment to production
set ENVIRONMENT=production

REM Run the deployment script
python deploy_to_production.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Production deployment completed successfully!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Production deployment failed!
    echo ========================================
)

pause

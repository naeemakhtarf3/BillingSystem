@echo off
echo Searching for Python installation...

REM Try different Python commands
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found: python
    python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
    goto :end
)

python3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found: python3
    python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
    goto :end
)

py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found: py
    py -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
    goto :end
)

REM Try to find Python in common locations
for %%i in (C:\Python*\python.exe C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python*\python.exe C:\Program Files\Python*\python.exe) do (
    if exist "%%i" (
        echo Found: %%i
        "%%i" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
        goto :end
    )
)

echo No Python installation found!
echo Please install Python 3.8+ and try again.
echo You can download it from: https://www.python.org/downloads/
pause

:end

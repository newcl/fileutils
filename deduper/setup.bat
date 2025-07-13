@echo off
echo Setting up deduper CLI tool...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or later
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Installing deduper...
pip install -e .
if errorlevel 1 (
    echo Error: Failed to install deduper
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To use deduper:
echo 1. Activate the virtual environment: venv\Scripts\activate
echo 2. Run deduper: deduper scan /path/to/directory
echo.
echo Or use the launcher script: deduper.bat scan /path/to/directory
echo.
pause 
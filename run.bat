@echo off
REM Lyftr AI - Full-stack Assignment
REM Universal Website Scraper (MVP) + JSON Viewer
REM Windows batch script version

echo Setting up project...

REM Check if uv is installed
where uv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: uv is not installed. Please install it first:
    echo   curl -LsSf https://astral.sh/uv/install.sh | sh
    echo   Or: pip install uv
    exit /b 1
)

REM Create virtual environment using uv if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment with uv...
    uv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install Python dependencies
echo Installing Python dependencies...
uv pip install -r requirements.txt

REM Install Playwright browsers if needed
echo Installing Playwright browsers...
python -m playwright install chromium || echo Playwright browsers already installed or installation skipped

REM Install frontend dependencies if needed
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

REM Build frontend
echo Building frontend...
cd frontend
call npm run build
cd ..

REM Start the server
echo Starting server on http://localhost:8000...
echo.
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload


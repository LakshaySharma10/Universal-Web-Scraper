@echo off
REM Lyftr AI - Full-stack Assignment
REM Universal Website Scraper (MVP) + JSON Viewer
REM Windows batch script version

echo Setting up project...

REM Find or install uv
set "UV_CMD="
where uv >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "UV_CMD=uv"
) else (
    echo uv is not installed. Installing uv automatically...
    echo This may take a minute...
    echo.
    
    REM Install uv using PowerShell
    powershell -ExecutionPolicy Bypass -Command "Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression"
    
    REM Check common installation paths
    if exist "%USERPROFILE%\.cargo\bin\uv.exe" (
        set "UV_CMD=%USERPROFILE%\.cargo\bin\uv.exe"
        echo Found uv at: %UV_CMD%
    ) else if exist "%USERPROFILE%\.local\bin\uv.exe" (
        set "UV_CMD=%USERPROFILE%\.local\bin\uv.exe"
        echo Found uv at: %UV_CMD%
    ) else (
        REM Try checking PATH again after installation
        where uv >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            set "UV_CMD=uv"
        ) else (
            echo.
            echo Error: uv installation may have failed or uv is not in the expected location.
            echo Please install uv manually:
            echo   powershell -ExecutionPolicy Bypass -Command "Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression"
            echo Then close and reopen your terminal and run this script again.
            echo.
            pause
            exit /b 1
        )
    )
    
    echo uv has been successfully installed!
    echo.
)

REM Create virtual environment using uv if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment with uv...
    "%UV_CMD%" venv
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to create virtual environment with uv.
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install Python dependencies
echo Installing Python dependencies...
"%UV_CMD%" pip install -r requirements.txt

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
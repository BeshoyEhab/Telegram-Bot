REM =============================================================================
REM FILE: setup.bat
REM DESCRIPTION: Automated setup script for Windows
REM LOCATION: Project root directory
REM PURPOSE: Automates installation, venv creation, database setup
REM USAGE: Double-click or run: setup.bat
REM =============================================================================

@echo off
REM Telegram School Bot - Setup Script for Windows

echo ==========================================
echo Telegram School Bot - Setup
echo ==========================================
echo.

REM Check Python
echo Checking Python version...
python --version
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo [OK] Python found
echo.

REM Create virtual environment
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [SKIP] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip > nul 2>&1
echo [OK] Pip upgraded
echo.

REM Install dependencies
echo Installing dependencies (this may take a few minutes)...
pip install -r requirements.txt
echo [OK] Dependencies installed
echo.

REM Check .env file
if not exist ".env" (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo.
    echo [IMPORTANT] Please edit .env file and add:
    echo   1. Your BOT_API token
    echo   2. Your Telegram user ID in USERS variable
    echo.
    pause
) else (
    echo [OK] .env file exists
)
echo.

REM Create directories
echo Creating necessary directories...
if not exist "logs\" mkdir logs
if not exist "backups\" mkdir backups
if not exist "exports\" mkdir exports
if not exist "templates\" mkdir templates
if not exist "database\migrations\versions\" mkdir database\migrations\versions
echo [OK] Directories created
echo.

REM Initialize database
echo Initializing database...
python -c "from database import init_db; init_db()"
echo [OK] Database initialized
echo.

REM Create initial migration
echo Creating initial migration...
alembic revision --autogenerate -m "Initial migration"
echo [OK] Migration created
echo.

REM Apply migrations
echo Applying migrations...
alembic upgrade head
echo [OK] Migrations applied
echo.

REM Test database
echo Testing database connection...
python -c "from database import check_connection; exit(0 if check_connection() else 1)"
if errorlevel 1 (
    echo [ERROR] Database connection failed
    pause
    exit /b 1
)
echo [OK] Database connection successful
echo.

REM Test configuration
echo Testing configuration...
python -c "import config; print('Bot Token:', config.BOT_API[:10] + '...'); print('Users:', len(config.AUTHORIZED_USERS))"
echo [OK] Configuration loaded
echo.

echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit .env file and add your BOT_API token
echo 2. Add your Telegram ID to USERS in .env
echo 3. Run: python main.py
echo.
echo To activate virtual environment later:
echo   venv\Scripts\activate.bat
echo.
pause

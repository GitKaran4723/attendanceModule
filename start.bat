@echo off
echo ========================================
echo  BCA BUB - Attendance System Setup
echo ========================================
echo.

echo [1/5] Verifying Python installation...
python --version
if %errorlevel% neq 0 (
    echo Error: Python not found! Please install Python 3.7+
    pause
    exit /b 1
)
echo.

echo [2/5] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing dependencies!
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

echo [3/5] Verifying setup...
python verify_setup.py
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Setup verification found issues
    echo Please fix them before continuing
    pause
    exit /b 1
)
echo.

echo [4/5] Generating app icons (optional)...
pip install Pillow >nul 2>&1
python generate_icons.py
echo.

echo [5/5] Starting Flask application...
echo.
echo ========================================
echo  🚀 BCA BUB Attendance System
echo ========================================
echo  📱 Access on this computer:
echo     http://localhost:5000
echo.
echo  📱 Access from mobile device:
echo     http://YOUR-IP-ADDRESS:5000
echo     (Find your IP using: ipconfig)
echo.
echo  ⚠️  Running in DEBUG mode
echo  ⏹️  Press Ctrl+C to stop
echo ========================================
echo.

python app.py

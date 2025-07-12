@echo off
echo Setting up ML Backend Data Sync System...
echo.

REM Change to ml_backend directory
cd /d "%~dp0ml_backend"

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Test the system
echo Testing the system...
python test_system.py

echo.
echo Setup completed! 
echo.
echo To start the system:
echo 1. Start API server: python start_api.py
echo 2. Test data sync: python sync_data.py
echo 3. Enable auto-sync: python sync_data.py --auto
echo 4. Test API health: curl http://localhost:5000/api/health
echo.
pause

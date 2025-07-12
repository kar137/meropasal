@echo off
echo Starting Flutter Data Sync Demo...
echo.

REM Change to Flutter app directory
cd /d "%~dp0meropasalapp"

REM Get Flutter dependencies
echo Getting Flutter dependencies...
flutter pub get

REM Check Flutter setup
echo Checking Flutter setup...
flutter doctor --version

echo.
echo Flutter app is ready!
echo.
echo To run the app:
echo 1. flutter run (for development)
echo 2. flutter run -d windows (for Windows desktop)
echo 3. flutter run -d chrome (for web)
echo.
echo Make sure the ML Backend API is running first:
echo cd ml_backend
echo python start_api.py
echo.
pause

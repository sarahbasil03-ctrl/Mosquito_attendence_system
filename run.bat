@echo off
title Mosquito Attendance System - Backend
color 0A

echo.
echo  =====================================================
echo    MOSQUITO ATTENDANCE SYSTEM  -  AI Backend
echo  =====================================================
echo.
echo  Checking Python...
python --version
if errorlevel 1 (
    echo.
    echo  ERROR: Python not found. Please install Python 3.8+
    echo  Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo  Installing / verifying dependencies...
python -m pip install flask flask-cors opencv-python numpy scipy --quiet
echo  Dependencies OK.

echo.
echo  =====================================================
echo    Starting server at: http://localhost:5000
echo    Open your browser to:
echo    http://localhost:5000
echo  =====================================================
echo.
echo  Press Ctrl+C to stop the server.
echo.

cd /d "%~dp0"
python app.py

pause

@echo off
echo Starting Flood Risk App...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start the Flask application
python app.py

pause

@echo off
echo Starting BuiltByRAVE CFO OS Chatbot...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if requirements.txt exists
if not exist "rag-backend\requirements.txt" (
    echo ERROR: requirements.txt not found
    pause
    exit /b 1
)

REM Install requirements
echo Installing Python requirements...
python -m pip install -r rag-backend\requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

REM Start the chatbot
echo Starting chatbot...
cd rag-backend
python chatbot.py
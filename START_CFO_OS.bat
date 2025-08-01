@echo off
title BuiltByRays™ CFO OS - Starting...
color 0A

echo.
echo ========================================
echo 🏢 BuiltByRays™ CFO OS
echo ========================================
echo 🚀 Starting automatically...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://python.org/downloads/
    echo.
    echo After installing Python, run this file again.
    echo.
    pause
    exit /b 1
)

REM Check if Node.js is installed (optional)
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Node.js not found - Electron app will be skipped
    echo You can install Node.js from: https://nodejs.org/
    echo.
) else (
    echo ✅ Node.js found
)

echo.
echo 🚀 Starting BuiltByRays™ CFO OS...
echo.

REM Run the automatic startup script
python auto_start.py

echo.
echo ========================================
echo 🎉 BuiltByRays™ CFO OS has started!
echo ========================================
echo.
echo 📱 Your application is now running at:
echo    • Web Interface: http://localhost:5000
echo    • Desktop App: Check for Electron window
echo.
echo ⚠️  Don't forget to add your OpenAI API key to the .env file
echo.
echo Press any key to exit...
pause >nul 
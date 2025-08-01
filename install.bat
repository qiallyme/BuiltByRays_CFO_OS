@echo off
setlocal enabledelayedexpansion

echo ========================================
echo BuiltByRAVE CFO OS - Windows Installer
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running with administrator privileges
) else (
    echo ⚠️  Not running as administrator - some features may be limited
)

echo.
echo 📋 Checking prerequisites...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Installing Python...
    echo Please download and install Python 3.8+ from https://python.org
    echo After installation, run this installer again.
    pause
    exit /b 1
) else (
    echo ✅ Python found
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Installing Node.js...
    echo Please download and install Node.js 16+ from https://nodejs.org
    echo After installation, run this installer again.
    pause
    exit /b 1
) else (
    echo ✅ Node.js found
)

echo.
echo 🚀 Starting installation...

REM Install Python requirements
echo 📦 Installing Python requirements...
python -m pip install --upgrade pip
python -m pip install -r rag-backend\requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python requirements
    pause
    exit /b 1
)
echo ✅ Python requirements installed

REM Install Node.js dependencies
echo 📦 Installing Node.js dependencies...
cd electron-app
npm install
if errorlevel 1 (
    echo ❌ Failed to install Node.js dependencies
    pause
    exit /b 1
)
cd ..
echo ✅ Node.js dependencies installed

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 🔧 Creating .env file...
    echo # BuiltByRAVE CFO OS Configuration > .env
    echo OPENAI_API_KEY=your_openai_api_key_here >> .env
    echo FLASK_ENV=development >> .env
    echo FLASK_DEBUG=True >> .env
    echo ✅ .env file created
    echo ⚠️  Please add your OpenAI API key to the .env file
) else (
    echo ✅ .env file already exists
)

REM Create desktop shortcuts
echo 🖥️  Creating desktop shortcuts...
set SCRIPT="%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%
echo sLinkFile = "%USERPROFILE%\Desktop\BuiltByRAVE CFO OS.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%~dp0start_cfo_os.bat" >> %SCRIPT%
echo oLink.WorkingDirectory = "%~dp0" >> %SCRIPT%
echo oLink.Description = "BuiltByRAVE CFO OS" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%
cscript //nologo %SCRIPT%
del %SCRIPT%

echo.
echo ========================================
echo 🎉 Installation completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Add your OpenAI API key to the .env file
echo 2. Double-click "BuiltByRAVE CFO OS" on your desktop
echo 3. Or run start_cfo_os.bat to start manually
echo.
echo For support: support@builtbyrave.com
echo ========================================
pause 
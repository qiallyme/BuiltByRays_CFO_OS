@echo off
echo ========================================
echo BuiltByRays™ CFO OS - Build Installer
echo ========================================
echo.

echo [1/6] Installing Python dependencies...
pip install -r rag-backend/requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)

echo.
echo [2/6] Installing Node.js dependencies...
cd electron-app
npm install
if errorlevel 1 (
    echo ERROR: Failed to install Node.js dependencies
    pause
    exit /b 1
)
cd ..

echo.
echo [3/6] Running setup script...
python setup.py
if errorlevel 1 (
    echo ERROR: Setup script failed
    pause
    exit /b 1
)

echo.
echo [4/6] Building Electron application...
npm run build
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo [5/6] Creating installer...
echo Build completed successfully!
echo.

echo [6/6] Installer location:
echo The installer can be found in the 'dist' folder
echo.

echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo The installer will:
echo - Install all necessary components
echo - Set up auto-startup on Windows boot
echo - Create desktop and start menu shortcuts
echo - Run with administrator privileges
echo.
echo Installer file: dist\BuiltByRays™ CFO OS Setup.exe
echo.
pause 
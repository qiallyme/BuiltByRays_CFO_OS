@echo off
echo ========================================
echo BuiltByRays™ CFO OS - Portable Package
echo ========================================
echo.

echo [1/5] Creating distribution directory...
if exist "dist-portable" rmdir /s /q "dist-portable"
mkdir "dist-portable"
mkdir "dist-portable\BuiltByRays-CFO-OS"

echo [2/5] Copying application files...
xcopy "electron-app\*" "dist-portable\BuiltByRays-CFO-OS\electron-app\" /E /I /Y
copy "main.js" "dist-portable\BuiltByRays-CFO-OS\"

echo [3/5] Copying backend and resources...
xcopy "rag-backend" "dist-portable\BuiltByRays-CFO-OS\rag-backend\" /E /I /Y
xcopy "vault" "dist-portable\BuiltByRays-CFO-OS\vault\" /E /I /Y
copy "VaultSyncDaemon.exe" "dist-portable\BuiltByRays-CFO-OS\"
copy "start_chatbot.py" "dist-portable\BuiltByRays-CFO-OS\"
copy "setup.py" "dist-portable\BuiltByRays-CFO-OS\"
copy ".env" "dist-portable\BuiltByRays-CFO-OS\"

echo [4/5] Creating startup scripts...
echo @echo off > "dist-portable\BuiltByRays-CFO-OS\START_CFO_OS.bat"
echo echo Starting BuiltByRays™ CFO OS... >> "dist-portable\BuiltByRays-CFO-OS\START_CFO_OS.bat"
echo echo. >> "dist-portable\BuiltByRays-CFO-OS\START_CFO_OS.bat"
echo echo Installing dependencies... >> "dist-portable\BuiltByRays-CFO-OS\START_CFO_OS.bat"
echo python setup.py >> "dist-portable\BuiltByRays-CFO-OS\START_CFO_OS.bat"
echo echo. >> "dist-portable\BuiltByRays-CFO-OS\START_CFO_OS.bat"
echo echo Starting backend services... >> "dist-portable\BuiltByRays-CFO-OS\START_CFO_OS.bat"
echo start "" python start_chatbot.py >> "dist-portable\BuiltByRays-CFO-OS\START_CFO_OS.bat"
echo start "" VaultSyncDaemon.exe >> "dist-portable\BuiltByRays-CFO-OS\START_CFO_OS.bat"
echo echo. >> "dist-portable\BuiltByRays-CFO-OS\START_CFO_OS.bat"
echo echo Starting Electron application... >> "dist-portable\BuiltByRays-CFO-OS\START_CFO_OS.bat"
echo cd electron-app >> "dist-portable\BuiltByRays-CFO-OS\START_CFO_OS.bat"
echo npm start >> "dist-portable\BuiltByRays-CFO-OS\START_CFO_OS.bat"
echo pause >> "dist-portable\BuiltByRays-CFO-OS\START_CFO_OS.bat"

echo [5/5] Creating auto-startup configuration...
echo @echo off > "dist-portable\BuiltByRays-CFO-OS\SETUP_AUTOSTART.bat"
echo echo Setting up auto-startup for BuiltByRays™ CFO OS... >> "dist-portable\BuiltByRays-CFO-OS\SETUP_AUTOSTART.bat"
echo echo. >> "dist-portable\BuiltByRays-CFO-OS\SETUP_AUTOSTART.bat"
echo reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "BuiltByRaysCFOOS" /t REG_SZ /d "%~dp0START_CFO_OS.bat" /f >> "dist-portable\BuiltByRays-CFO-OS\SETUP_AUTOSTART.bat"
echo echo Auto-startup configured successfully! >> "dist-portable\BuiltByRays-CFO-OS\SETUP_AUTOSTART.bat"
echo pause >> "dist-portable\BuiltByRays-CFO-OS\SETUP_AUTOSTART.bat"

echo.
echo ========================================
echo Package created successfully!
echo ========================================
echo.
echo Location: dist-portable\BuiltByRays-CFO-OS\
echo.
echo To install for client:
echo 1. Copy the entire "BuiltByRays-CFO-OS" folder to client's computer
echo 2. Run SETUP_AUTOSTART.bat as administrator to enable auto-startup
echo 3. Run START_CFO_OS.bat to start the application
echo.
echo The application will:
echo - Install all dependencies automatically
echo - Start backend services (Python chatbot, vault sync)
echo - Launch the Electron interface
echo - Configure auto-startup on Windows boot
echo.
pause 
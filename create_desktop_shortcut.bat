@echo off
echo Creating desktop shortcut for BuiltByRays™ CFO OS...

REM Create VBScript to create shortcut
set SCRIPT="%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%
echo sLinkFile = "%USERPROFILE%\Desktop\BuiltByRays™ CFO OS.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%~dp0START_CFO_OS.bat" >> %SCRIPT%
echo oLink.WorkingDirectory = "%~dp0" >> %SCRIPT%
echo oLink.Description = "BuiltByRays™ CFO OS - One-Click Startup" >> %SCRIPT%
echo oLink.IconLocation = "%~dp0electron-app\assets\logo.png" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%

REM Execute the script
cscript //nologo %SCRIPT%
del %SCRIPT%

echo.
echo ✅ Desktop shortcut created successfully!
echo.
echo You can now double-click "BuiltByRays™ CFO OS" on your desktop
echo to start the application automatically.
echo.
pause 
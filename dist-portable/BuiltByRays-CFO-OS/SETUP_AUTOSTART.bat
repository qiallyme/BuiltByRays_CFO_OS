@echo off 
echo Setting up auto-startup for BuiltByRays™ CFO OS... 
echo. 
reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "BuiltByRaysCFOOS" /t REG_SZ /d "C:\Users\codyr\Documents\Github\EmpowerQNow713\BuiltByRays_CFO_OS\START_CFO_OS.bat" /f 
echo Auto-startup configured successfully! 
pause 

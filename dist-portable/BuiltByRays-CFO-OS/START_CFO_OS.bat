@echo off 
echo Starting BuiltByRays™ CFO OS... 
echo. 
echo Installing dependencies... 
python setup.py 
echo. 
echo Starting backend services... 
start "" python start_chatbot.py 
start "" VaultSyncDaemon.exe 
echo. 
echo Starting Electron application... 
cd electron-app 
npm start 
pause 

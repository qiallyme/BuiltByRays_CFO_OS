@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

rem ===== CONFIG =====
set "BASE=%~dp0"
set "CONTENT=%BASE%content"
set "PY=python"
set "DEFAULT_MSG=KB: update TOC, tags, build"

echo === BuiltByRays KB - All In One ===
echo Repo: %BASE%
echo CONTENT=%CONTENT%
echo.

rem ---- Sanity checks ----
echo [sanity] checking content folder...
if not exist "%CONTENT%" (
  echo ERROR: content folder NOT found: "%CONTENT%"
  dir "%BASE%"
  exit /b 1
)
echo [sanity] checking Python/Node/NPX...
where %PY% >nul 2>nul || (echo ERROR: Python not found on PATH.& exit /b 1)
node -v >nul 2>nul || (echo ERROR: Node.js not found on PATH.& exit /b 1)
npx -v  >nul 2>nul || (echo ERROR: NPX not found on PATH.& exit /b 1)

echo.
echo [1/6] Normalize + tags + related...
call "%PY%" ".\kb_autotag_backlink.py" --base ".\content" --apply || goto :fail

echo [2/6] Generate TOCs + global index...
if exist ".\kb_toc_and_tags.py" call "%PY%" ".\kb_toc_and_tags.py" --base ".\content" --apply

echo [3/6] Validate...
if exist ".\kb_validate.py" call "%PY%" ".\kb_validate.py" --base ".\content" --strict

echo [4/6] Install deps if needed...
if not exist "node_modules" (
  call npm ci || goto :fail
) else (
  echo node_modules present - skipping install
)

echo [5/6] Build Quartz...
call npx quartz build || goto :fail
if exist "public\index.html" copy /Y "public\index.html" "public\404.html" >nul

echo [6/6] Local preview...
set "PORT="
for /l %%P in (8080,1,8090) do (
  powershell -NoProfile -Command "if ((Test-NetConnection -ComputerName 127.0.0.1 -Port %%P -InformationLevel Quiet)) { exit 0 } else { exit 1 }" >nul 2>nul
  if errorlevel 1 (
    set "PORT=%%P"
    goto :have_port
  )
)
set "PORT=8080"
:have_port

start "Preview" cmd /c "npx serve public -l %PORT%"
echo Waiting for http://localhost:%PORT% to come up...
powershell -NoProfile -Command "$u='http://localhost:%PORT%'; for($i=0;$i -lt 40;$i++){ try{ (Invoke-WebRequest -UseBasicParsing $u).StatusCode | Out-Null; exit 0 } catch{} Start-Sleep -Milliseconds 300 }; exit 1" >nul 2>nul

start "" "http://localhost:%PORT%"
echo Press any key AFTER you're done reviewing in the browser...
pause >nul

set /p PUSH="Push changes to Git? (Y/N): "
if /i "%PUSH%"=="Y" (
  set /p MSG="Commit message (blank = default): "
  if "%MSG%"=="" set "MSG=%DEFAULT_MSG%"
  git add -A
  git commit -m "%MSG%" || echo No changes to commit.
  git push
) else (
  echo Skipping push.
)

echo Done.
exit /b 0

:fail
echo Build failed (see messages above).
exit /b 1

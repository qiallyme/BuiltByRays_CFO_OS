@echo off
setlocal EnableExtensions
chcp 65001 >nul

REM ===== CONFIG =====
set "BASE=%~dp0"
cd /d "%BASE%"
set "CONTENT=%BASE%content"
set "PY=python"
set "DEFAULT_MSG=KB: update TOC, tags, build"

echo === BuiltByRays KB - All In One (lean) ===
echo Repo: %BASE%
echo CONTENT=%CONTENT%
echo.

REM ---- 1) Fix frontmatter (dedupe/normalize) ----
echo [1/5] Fix frontmatter...
if exist "kb_fix_frontmatter.py" (
  call "%PY%" "kb_fix_frontmatter.py" --base ".\content" --apply || goto :fail
) else (
  echo   (skip: kb_fix_frontmatter.py not found)
)

REM ---- 2) Auto-tagging + backlinks ----
echo [2/5] Auto-tagging + backlinks...
if exist "kb_autotag_backlink.py" (
  call "%PY%" "kb_autotag_backlink.py" --base ".\content" --apply || goto :fail
) else (
  echo   (skip: kb_autotag_backlink.py not found)
)

REM ---- 3) TOC + global index ----
echo [3/5] TOC + global index...
if exist "kb_toc_and_tags.py" (
  call "%PY%" "kb_toc_and_tags.py" --base ".\content" --apply || goto :fail
) else (
  echo   (skip: kb_toc_and_tags.py not found)
)

REM ---- 4) Build Quartz ----
echo [4/5] Building Quartz...
call npx quartz build || goto :fail
if exist "public\index.html" copy /Y "public\index.html" "public\404.html" >nul

REM ---- 5) Preview (pick open port 8080-8090), then push ----
echo [5/5] Starting preview...
set "PORT="
for /l %%P in (8080,1,8090) do (
  powershell -NoProfile -Command "exit ((Test-NetConnection -ComputerName 127.0.0.1 -Port %%P -InformationLevel Quiet) ? 0 : 1)" >nul 2>nul
  if errorlevel 1 (
    set "PORT=%%P"
    goto :have_port
  )
)
set "PORT=8080"
:have_port
start "Preview" cmd /c "npx serve public -l %PORT%"
start "" "http://localhost:%PORT%"
echo   preview on http://localhost:%PORT%
echo.
echo Press any key AFTER you finish reviewing...
pause >nul

echo Push changes to Git? (Y/N)
set /p PUSH="> "
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
echo.
echo Build failed (see messages above).
exit /b 1

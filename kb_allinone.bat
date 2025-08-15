@echo off
setlocal EnableExtensions
chcp 65001 >nul

REM ===== Basics =====
set "BASE=%~dp0"
cd /d "%BASE%"
set "PY=python"
set "DEFAULT_MSG=KB: clean rebuild + content update"

echo === BuiltByRays KB - All In One ===
echo Repo: %BASE%
echo.

REM 0) Kill any leftover preview servers
taskkill /im node.exe /f >nul 2>nul

REM 0.5) Clean output & caches for a truly fresh build
echo [0] Cleaning output/cache...
if exist "public" rmdir /s /q "public"
if exist ".quartz-cache" rmdir /s /q ".quartz-cache"
if exist "quartz\.cache" rmdir /s /q "quartz\.cache"
if exist ".cache" rmdir /s /q ".cache"
if exist "node_modules\.cache" rmdir /s /q "node_modules\.cache"

REM 1) Cleanup any old duplicated headers/blocks
if exist "kb_cleanup_headers.py" (
  echo [1] Cleanup headers/old blocks...
  call "%PY%" "kb_cleanup_headers.py" --base ".\content" --apply || goto :fail
) else (
  echo [1] Skip cleanup (kb_cleanup_headers.py not found)
)

REM 1.5) Fix frontmatter after cleanup
echo [1.5] Fix frontmatter (post-cleanup)...
call "%PY%" "kb_fix_frontmatter.py" --base ".\content" --apply || goto :fail

REM 2) Auto-tagging + backlinks (YAML now limits tags)
if exist "kb_autotag_backlink.py" (
  echo [2] Auto-tag + backlinks...
  call "%PY%" "kb_autotag_backlink.py" --base ".\content" --apply || goto :fail
) else (
  echo [2] Skip autotag (kb_autotag_backlink.py not found)
)

REM 2.5) Fix frontmatter after autotag
echo [2.5] Fix frontmatter (post-autotag)...
call "%PY%" "kb_fix_frontmatter.py" --base ".\content" --apply || goto :fail

REM 3) Global index + per-folder TOCs (structure only)
if exist "kb_toc_and_tags.py" (
  echo [3] TOC + global index...
  call "%PY%" "kb_toc_and_tags.py" --base ".\content" --apply || goto :fail
) else (
  echo [3] Skip TOC (kb_toc_and_tags.py not found)
)

REM 3.5) Fix frontmatter after TOC
echo [3.5] Fix frontmatter (post-TOC)...
call "%PY%" "kb_fix_frontmatter.py" --base ".\content" --apply || goto :fail

REM 4) FINAL frontmatter/H1 pass (dedupe + keep A./B. prefixes)
echo [4] Fix frontmatter + H1 (final)...
call "%PY%" "kb_fix_frontmatter.py" --base ".\content" --apply || goto :fail

REM 5) Build Quartz (fresh)
echo [5] Build Quartz...
call npx quartz build || goto :fail
if exist "public\index.html" copy /Y "public\index.html" "public\404.html" >nul

REM 6) Preview
echo [6] Previewing...
set "PORT="
for /l %%P in (8080,1,8090) do (
  powershell -NoProfile -Command "exit ((Test-NetConnection -ComputerName 127.0.0.1 -Port %%P -InformationLevel Quiet) ? 0 : 1)" >nul 2>nul
  if errorlevel 1 ( set "PORT=%%P" & goto :have_port )
)
set "PORT=8080"
:have_port
start "Preview" cmd /c "npx serve public -l %PORT%"
start "" "http://localhost:%PORT%"
echo Opened http://localhost:%PORT%
echo Press any key AFTER you finish reviewing...
pause >nul

REM 7) Push
echo [7] Push to Git? (Y/N)
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
echo Build failed.
exit /b 1

@echo on
setlocal EnableExtensions EnableDelayedExpansion
title BuiltByRays KB - All In One
chcp 65001 >nul

REM ===== CONFIG =====
set "BASE=%~dp0"
set "CONTENT=%BASE%content"
set "PY=python"
set "DEFAULT_MSG=KB: update TOC, tags, build"
set "START_PORT=8080"
set "END_PORT=8090"

echo.
echo === BuiltByRays KB - All In One ===
echo Repo: %BASE%
echo CONTENT=%CONTENT%
echo.

REM ---- Sanity checks ----
if not exist "%CONTENT%" (
  echo ERROR: content folder NOT found: "%CONTENT%"
  dir "%BASE%"
  exit /b 1
)
where %PY% || (echo ERROR: Python not found on PATH.& exit /b 1)
node -v  || (echo ERROR: Node.js not found on PATH.& exit /b 1)
npx  -v  || (echo ERROR: NPX not found on PATH.& exit /b 1)

REM ---- 1) TOC + titles/tags + H1 ----
echo [1/8] TOC and titles/tags...
"%PY%" "%BASE%kb_toc_and_tags.py" --base "%CONTENT%" --apply
if errorlevel 1 echo WARN: kb_toc_and_tags exited with code %ERRORLEVEL%

REM ---- 2) Auto-smart tags + backlinks ----
echo [2/8] Auto-tagging and backlinks...
"%PY%" "%BASE%kb_autotag_backlink.py" --base "%CONTENT%" --apply
if errorlevel 1 echo WARN: auto-tagger returned non-zero (continuing)

REM ---- 3) Frontmatter cleanup ----
echo [3/8] Frontmatter cleanup...
"%PY%" "%BASE%kb_fix_frontmatter.py"
if errorlevel 1 echo WARN: kb_fix_frontmatter exited with code %ERRORLEVEL%

REM ---- 4) Validate for Quartz ----
echo [4/8] Validating markdown/frontmatter...
"%PY%" "%BASE%kb_validate.py" --base "%CONTENT%"
if errorlevel 2 (
  echo ERROR: Blocking validation errors. Fix and re-run.
  exit /b 2
)
if errorlevel 1 (
  echo WARN: Validation warnings detected. Continue? Y or N
  choice /c YN /n
  if errorlevel 2 exit /b 1
)

REM ---- 5) Ensure node deps ----
echo [5/8] Checking node_modules...
if exist "%BASE%node_modules" (
  echo node_modules present - skipping install
) else (
  call npm install
  if errorlevel 1 (
    echo ERROR: npm install failed.
    exit /b 1
  )
)

REM ---- 6) Build Quartz (retry after cache clean if needed) ----
echo [6/8] Building Quartz...
call npx quartz build
if errorlevel 1 (
  echo WARN: Quartz build failed, cleaning cache and retrying...
  if exist "%BASE%.quartz" rmdir /s /q "%BASE%.quartz"
  call npx quartz build
  if errorlevel 1 (
    echo ERROR: Quartz build failed again. Check errors above.
    exit /b 1
  )
)

REM ---- 7) Preview (auto-port). Run in THIS window so we see logs. Fallback to static serve. ----
set "PORT="
for /l %%P in (%START_PORT%,1,%END_PORT%) do (
  powershell -NoProfile -Command "$c=Get-NetTCPConnection -LocalPort %%P -ErrorAction SilentlyContinue; if($null -eq $c){exit 0}else{exit 1}" >nul 2>&1
  if !errorlevel!==0 (
    set "PORT=%%P"
    goto :port_found
  )
)
:port_found
if "%PORT%"=="" set "PORT=%START_PORT%"

echo Starting Quartz preview on http://localhost:%PORT% ...
call npx quartz preview --port %PORT%
if errorlevel 1 (
  echo WARN: Quartz preview failed or exited. Trying static server on %PORT%...
  call npx serve public -l %PORT%
  if errorlevel 1 (
    echo ERROR: Static server failed too. Check logs above.
    exit /b 1
  )
)

echo Press any key AFTER you finish reviewing in the browser...
pause >nul

REM ---- 8) Commit + Push ----
echo [8/8] Push changes to Git? Y or N
choice /c YN /n
if errorlevel 2 (
  echo Skipping push. Done.
  exit /b 0
)

set "MSG="
set /p "MSG=Enter commit message (or leave blank to use default): "
if "%MSG%"=="" set "MSG=%DEFAULT_MSG%"

git add -A
git commit -m "%MSG%"
if errorlevel 1 echo Nothing to commit or commit failed.
git push
if errorlevel 1 (
  echo ERROR: git push failed (remote/credentials?).
  exit /b 1
)

echo Done. Shipped.
exit /b 0

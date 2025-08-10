@echo off
setlocal EnableExtensions EnableDelayedExpansion
title BuiltByRays KB — All In One

REM ===== CONFIG =====
set "BASE=%~dp0"
set "CONTENT=%BASE%content"
set "PY=python"
set "PORT=8080"
set "DEFAULT_MSG=KB: update TOC, tags, build"

echo.
echo === BuiltByRays KB — All In One ===
echo Repo: %BASE%
echo.

REM --- Sanity
if not exist "%CONTENT%" (
  echo ERROR: content folder not found: "%CONTENT%"
  exit /b 1
)
where %PY% >nul 2>&1 || (echo ERROR: Python not found on PATH.& exit /b 1)
node -v >nul 2>&1 || (echo ERROR: Node.js not found on PATH.& exit /b 1)

REM --- 1) TOC + titles/tags + inject H1
echo [1/7] TOC and titles/tags...
"%PY%" "%BASE%kb_toc_and_tags.py" --base "%CONTENT%" --apply

REM --- 2) Auto-smart tags + backlinks
echo [2/7] Auto-tagging and backlinks...
"%PY%" "%BASE%kb_autotag_backlink.py" --base "%CONTENT%" --apply
if errorlevel 1 echo WARN: auto-tagger returned non-zero (continuing)

REM --- 3) Frontmatter cleanup (fix YAML lists, normalize tags)
echo [3/7] Frontmatter cleanup...
"%PY%" "%BASE%kb_fix_frontmatter.py"

REM --- 4) Validate for Quartz
echo [4/7] Validating markdown/frontmatter...
"%PY%" "%BASE%kb_validate.py" --base "%CONTENT%"
if errorlevel 2 (
  echo ERROR: Blocking validation errors. Fix and re-run.
  exit /b 2
)
if errorlevel 1 (
  echo WARN: Validation warnings. Continue? Y or N
  choice /c YN /n
  if errorlevel 2 exit /b 1
)

REM --- 5) Install deps if needed
echo [5/7] Checking node_modules...
if exist "%BASE%node_modules" (
  echo node_modules present - skipping install
) else (
  call npm install
  if errorlevel 1 (
    echo ERROR: npm install failed.
    exit /b 1
  )
)

REM --- 6) Build + Preview
echo [6/7] Building Quartz...
call npx quartz build
if errorlevel 1 (
  echo ERROR: Quartz build failed.
  exit /b 1
)

echo Starting preview on http://localhost:%PORT% ...
start "KB Preview" cmd /c "npx quartz preview --port %PORT%"
echo Press any key AFTER you finish reviewing the site in your browser...
pause >nul

REM --- 7) Commit + Push
echo [7/7] Push changes to Git? Y or N
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
if errorlevel 1 echo (Nothing to commit or commit failed.)
git push
if errorlevel 1 (
  echo ERROR: git push failed (remote/credentials?).
  exit /b 1
)

echo Done. Shipped.
exit /b 0

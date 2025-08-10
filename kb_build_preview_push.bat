@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM === CONFIG ===
set "BASE_DIR=%~dp0"
set "CONTENT_DIR=%BASE_DIR%content"
set "PY=python"
set "PORT=8080"
set "COMMIT_MSG=KB: auto-update TOC, validate, rebuild"

echo.
echo == QBOSS RUNNER ==
echo Repo: %BASE_DIR%
echo.

REM 0) sanity checks
if not exist "%CONTENT_DIR%" (
  echo ERROR: content folder not found: "%CONTENT_DIR%"
  exit /b 1
)

where %PY% >nul 2>&1
if errorlevel 1 (
  echo ERROR: Python not found on PATH.
  exit /b 1
)

node -v >nul 2>&1
if errorlevel 1 (
  echo ERROR: Node.js not found on PATH.
  exit /b 1
)

echo.
echo [1/5] Updating TOC and frontmatter...
"%PY%" "%BASE_DIR%kb_toc_and_tags.py" --base "%CONTENT_DIR%" --apply

echo.
echo [1.5/5] Auto-tagging and backlinks...
"%PY%" "%BASE_DIR%kb_autotag_backlink.py" --base "%CONTENT_DIR%" --apply
if errorlevel 1 (
  echo WARN: auto-tagging returned a non-zero code. Continuing...
)

echo.
echo [2/5] Validating Markdown and frontmatter...
"%PY%" "%BASE_DIR%kb_validate.py" --base "%CONTENT_DIR%"
if errorlevel 2 (
  echo ERROR: Validation found blocking issues.
  exit /b 2
)
if errorlevel 1 (
  echo WARN: Validation warnings detected. Continue? Y or N
  choice /c YN /n
  if errorlevel 2 exit /b 1
)

echo.
echo [3/5] Installing deps if needed...
if exist "%BASE_DIR%node_modules" (
  echo node_modules present - skipping install
) else (
  call npm install
  if errorlevel 1 (
    echo ERROR: npm install failed.
    exit /b 1
  )
)

echo.
echo [4/5] Building Quartz site...
call npx quartz build
if errorlevel 1 (
  echo ERROR: Quartz build failed.
  exit /b 1
)

echo.
echo [4.5/5] Previewing public on port %PORT% ...
REM Use start to launch serve in a new window
start "KB Preview" cmd /c "npx serve public -l %PORT%"
echo Press any key after you finish reviewing in the browser...
pause >nul

echo.
echo [5/5] Push to GitHub now? Y or N
choice /c YN /n
if errorlevel 2 (
  echo Skipping git push. Done.
  exit /b 0
)

git status -s
echo Proceed with commit: %COMMIT_MSG%  Y or N
choice /c YN /n
if errorlevel 2 (
  echo Commit cancelled.
  exit /b 0
)

git add -A
git commit -m "%COMMIT_MSG%"
if errorlevel 1 (
  echo WARN: Nothing to commit or commit failed.
)
git push
if errorlevel 1 (
  echo ERROR: git push failed. Check remote/credentials.
  exit /b 1
)

echo.
echo Done. TOC updated, validated, built, previewed, and pushed.
exit /b 0

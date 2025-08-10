# BuiltByRays KB - All In One (PS1)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$Host.UI.RawUI.WindowTitle = 'BuiltByRays KB - All In One (PS1)'

# --- Config ---
$BASE = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $BASE
$CONTENT = Join-Path $BASE "content"
$PY = "python"
$DEFAULT_MSG = "KB: update TOC, tags, build"
$START_PORT = 8080
$END_PORT   = 8090

Write-Host ""
Write-Host "=== BuiltByRays KB - All In One (PS1) ==="
Write-Host "Repo: $BASE"
Write-Host "CONTENT=$CONTENT"
Write-Host ""

# --- Helpers ---
function Run-Step {
  param([string]$label,[scriptblock]$action)
  Write-Host ""
  Write-Host $label
  & $action
  if ($LASTEXITCODE -ne 0) { throw "Step failed: $label (exit $LASTEXITCODE)" }
}

function Py {
  param([string[]]$argv)
  & $PY @($argv)
  if ($LASTEXITCODE -ne 0) { throw "Python failed: $($argv -join ' ')" }
}

function Test-PortFree {
  param([int]$Port)
  try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $tcp.Connect("127.0.0.1", $Port)
    $tcp.Close()
    return $false
  } catch {
    return $true
  }
}

# --- Sanity checks ---
if (-not (Test-Path $CONTENT)) { Write-Error "content folder not found: $CONTENT" }

$node = (& node -v) 2>$null
if (-not $node) { throw "Node.js not found on PATH." }
$npxv = (& npx -v) 2>$null
if (-not $npxv) { throw "NPX not found on PATH." }

# --- 1: TOC + titles/tags ---
Run-Step "[1/7] TOC and titles/tags..." {
  Py @(".\kb_toc_and_tags.py","--base",$CONTENT,"--apply")
}

# --- 2: Auto-tagging + backlinks ---
Run-Step "[2/7] Auto-tagging and backlinks..." {
  Py @(".\kb_autotag_backlink.py","--base",$CONTENT,"--apply")
}

# --- 3: Frontmatter cleanup ---
Run-Step "[3/7] Frontmatter cleanup..." {
  Py @(".\kb_fix_frontmatter.py","--base",$CONTENT,"--apply")
}

# --- 4: Validate content ---
Run-Step "[4/7] Validating markdown/frontmatter..." {
  Py @(".\kb_validate.py","--base",$CONTENT)
}

# --- 5: Ensure node deps ---
Run-Step "[5/7] Checking node_modules..." {
  if (-not (Test-Path (Join-Path $BASE "node_modules"))) {
    Write-Host "node_modules missing - running npm ci"
    npm ci
    if ($LASTEXITCODE -ne 0) { throw "npm ci failed" }
  } else {
    Write-Host "node_modules present - skipping install"
  }
}

# --- 6: Build + Preview ---
Run-Step "[6/7] Building Quartz..." {
  npx quartz build
  if ($LASTEXITCODE -ne 0) { throw "quartz build failed" }

  $port = $null
  foreach ($p in $START_PORT..$END_PORT) {
    if (Test-PortFree -Port $p) { $port = $p; break }
  }
  if (-not $port) { throw "No free port between $START_PORT and $END_PORT" }

  Write-Host "Starting preview on http://localhost:$port ..."
  $serve = Start-Process -FilePath "npx" -ArgumentList @("serve","public","-l",$port) -PassThru -WindowStyle Hidden
  try {
    Read-Host "Press Enter AFTER you finish reviewing the site in your browser"
  } finally {
    if ($serve -and -not $serve.HasExited) { Stop-Process -Id $serve.Id -Force }
  }
}

# --- 7: Git push ---
$ans = Read-Host "[7/7] Push changes to Git? Y or N"
if ($ans -match "^[Yy]") {
  $msg = Read-Host "Enter commit message (or leave blank to use default)"
  if ([string]::IsNullOrWhiteSpace($msg)) { $msg = $DEFAULT_MSG }
  git add .
  git commit -m $msg
  git push
} else {
  Write-Host "Skipping push. Done."
}

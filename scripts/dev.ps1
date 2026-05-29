param(
  [switch]$Install
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

& (Join-Path $PSScriptRoot "sync-env.ps1")

function Resolve-Python {
  $rootVenv = Join-Path $repoRoot ".venv\Scripts\python.exe"
  $backendVenv = Join-Path $repoRoot "backend\.venv\Scripts\python.exe"
  if (Test-Path $rootVenv) { return $rootVenv }
  if (Test-Path $backendVenv) { return $backendVenv }

  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($python) { return $python.Source }

  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) { return $py.Source }

  throw "Python was not found. Install Python or create .venv at the repository root."
}

function Resolve-FrontendCommand {
  $corepack = Get-Command corepack -ErrorAction SilentlyContinue
  if ($corepack) {
    return "corepack pnpm"
  }

  throw "Corepack was not found. Install Node.js with Corepack support, then run corepack enable."
}

$python = Resolve-Python
$frontendCommand = Resolve-FrontendCommand

if ($Install) {
  Write-Host "Installing backend dependencies..." -ForegroundColor Cyan
  & $python -m pip install -r backend\requirements.txt

  Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
  Push-Location frontend
  corepack pnpm install
  Pop-Location
}

$backendCommand = "Set-Location '$repoRoot\backend'; & '$python' -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
$frontendRun = "corepack pnpm dev"
$frontendCommandText = "Set-Location '$repoRoot\frontend'; $frontendRun"

Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $backendCommand -WorkingDirectory (Join-Path $repoRoot "backend")
Start-Sleep -Seconds 1
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $frontendCommandText -WorkingDirectory (Join-Path $repoRoot "frontend")

Write-Host "UrbanLens dev servers launching:" -ForegroundColor Green
Write-Host "  Backend:  http://localhost:8000"
Write-Host "  Frontend: http://localhost:3000"
Write-Host "Close the opened PowerShell windows to stop the servers."

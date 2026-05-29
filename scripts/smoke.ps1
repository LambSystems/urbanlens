$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
  $cmd = Get-Command python -ErrorAction SilentlyContinue
  if ($cmd) {
    $python = $cmd.Source
  } else {
    throw "Python was not found. Create .venv or install Python before running smoke checks."
  }
}

& (Join-Path $PSScriptRoot "sync-env.ps1")

Push-Location backend
try {
  & $python -m unittest discover tests
  & $python scripts\demo_analysis.py
} finally {
  Pop-Location
}

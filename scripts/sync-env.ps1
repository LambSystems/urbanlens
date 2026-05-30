param(
  [string]$RootEnvPath = ".env"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

$rootEnv = Join-Path $repoRoot $RootEnvPath
$rootExample = Join-Path $repoRoot ".env.example"

if (-not (Test-Path $rootEnv)) {
  if (-not (Test-Path $rootExample)) {
    throw "Missing .env and .env.example at repository root."
  }
  Copy-Item -LiteralPath $rootExample -Destination $rootEnv
  Write-Host "Created .env from .env.example. Fill API keys as needed." -ForegroundColor Yellow
}

$entries = New-Object System.Collections.Generic.List[string]
foreach ($line in Get-Content -LiteralPath $rootEnv) {
  $trimmed = $line.Trim()
  if ($trimmed -eq "" -or $trimmed.StartsWith("#")) {
    continue
  }
  if ($trimmed -notmatch "^[A-Za-z_][A-Za-z0-9_]*=") {
    continue
  }
  $entries.Add($trimmed)
}

$backendKeys = @(
  "LLM_PROVIDER",
  "DEMO_MODE",
  "ANTHROPIC_API_KEY",
  "ANTHROPIC_MODEL",
  "ANTHROPIC_VISION_MODEL",
  "GEMINI_API_KEY",
  "GEMINI_MODEL",
  "FEATHERLESS_API_KEY",
  "FEATHERLESS_MODEL",
  "FEATHERLESS_HTTP_REFERER",
  "FEATHERLESS_X_TITLE",
  "ELEVENLABS_API_KEY",
  "ELEVENLABS_VOICE_ID",
  "ELEVENLABS_MODEL_ID"
)

$frontendPrefix = "NEXT_PUBLIC_"
$backendLines = New-Object System.Collections.Generic.List[string]
$frontendLines = New-Object System.Collections.Generic.List[string]

foreach ($entry in $entries) {
  $key = $entry.Split("=", 2)[0]
  if ($backendKeys -contains $key) {
    $backendLines.Add($entry)
  }
  if ($key.StartsWith($frontendPrefix)) {
    $frontendLines.Add($entry)
  }
}

$backendEnv = Join-Path $repoRoot "backend\.env"
$frontendEnv = Join-Path $repoRoot "frontend\.env"

function Backup-ManualEnv {
  param(
    [string]$Path
  )

  if (-not (Test-Path $Path)) {
    return
  }

  $firstLine = Get-Content -LiteralPath $Path -TotalCount 1
  if ($firstLine -eq "# Generated from repository-root .env by scripts/sync-env.ps1.") {
    return
  }

  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  $backupPath = "$Path.manual-backup-$stamp"
  Copy-Item -LiteralPath $Path -Destination $backupPath
  Write-Host "Backed up existing manual env file to $backupPath" -ForegroundColor Yellow
}

Backup-ManualEnv -Path $backendEnv
Backup-ManualEnv -Path $frontendEnv

@(
  "# Generated from repository-root .env by scripts/sync-env.ps1."
  "# Edit ../../.env, then rerun scripts/sync-env.ps1."
  ""
) + $backendLines | Set-Content -LiteralPath $backendEnv -Encoding utf8

@(
  "# Generated from repository-root .env by scripts/sync-env.ps1."
  "# Edit ../.env, then rerun scripts/sync-env.ps1."
  ""
) + $frontendLines | Set-Content -LiteralPath $frontendEnv -Encoding utf8

Write-Host "Synced backend/.env and frontend/.env from $RootEnvPath." -ForegroundColor Green

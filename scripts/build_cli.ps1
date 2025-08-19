#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = Resolve-Path "$PSScriptRoot/.."
Set-Location $repoRoot

if (-not $env:SOURCE_DATE_EPOCH) { $env:SOURCE_DATE_EPOCH = "0" }

$versionLine = Select-String '^version = ' -Path pyproject.toml | Select-Object -First 1
$VERSION = ($versionLine -split '"')[1]
$COMMIT = (git rev-parse --short HEAD).Trim()
$env:COBRA_CLI_VERSION = $VERSION
$env:COBRA_CLI_COMMIT = $COMMIT
Write-Host "Construyendo Cobra CLI v$env:COBRA_CLI_VERSION (commit $env:COBRA_CLI_COMMIT)"

pip install --no-cache-dir -r requirements.txt

pyinstaller --onefile --clean --strip cobra-cli.spec

$artifactName = "cobra-cli"
if ($IsWindows) { $artifactName += ".exe" }
$artifact = Join-Path "dist" $artifactName
$HASH1 = (Get-FileHash $artifact -Algorithm SHA256).Hash.ToLower()
Write-Host "Primer hash: $HASH1"

Remove-Item -Recurse -Force build, dist
pyinstaller --onefile --clean --strip cobra-cli.spec
$HASH2 = (Get-FileHash $artifact -Algorithm SHA256).Hash.ToLower()
Write-Host "Segundo hash: $HASH2"

if ($HASH1 -ne $HASH2) {
    Write-Error "Error: los hashes no coinciden"
    exit 1
}

Write-Host "Hash verificado: $HASH1"

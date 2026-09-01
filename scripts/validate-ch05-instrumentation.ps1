$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

python src/north_garden/validate_ch05_instrumentation_suite.py
if ($LASTEXITCODE -ne 0) { throw 'Offline CH05 instrumentation validation failed.' }

Write-Host 'Offline CH05 instrumentation validation passed. No provider call or upload was made.'

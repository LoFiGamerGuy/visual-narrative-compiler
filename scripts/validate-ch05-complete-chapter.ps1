$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

python src/north_garden/validate_ch05_complete_chapter.py @args
if ($LASTEXITCODE -ne 0) { throw 'CH05 complete-chapter manifest validation failed.' }

Write-Host 'CH05 complete-chapter manifest validation passed. No provider call or upload was made.'

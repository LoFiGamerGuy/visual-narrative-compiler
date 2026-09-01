param(
    [ValidateSet('documentation', 'baseline_legacy', 'blender_stage')]
    [string]$Profile = 'documentation',
    [switch]$WriteLocalRuntimeTemplate
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
    Write-Host 'Created .env from .env.example; fill credentials only if you choose to run an external adapter.'
}

$template = 'config/runtime-assets.example.json'
$local = 'config/runtime-assets.local.json'
if ($WriteLocalRuntimeTemplate -and -not (Test-Path $local)) {
    Copy-Item $template $local
    Write-Host "Created $local. Fill exact source URLs, hashes, and license artifacts; this script never downloads models."
}

$required = switch ($Profile) {
    'documentation' { @('python') }
    'baseline_legacy' { @('python', 'ComfyUI', 'models', 'loras') }
    'blender_stage' { @('python') }
}
foreach ($entry in $required) {
    if ($entry -eq 'python') {
        if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw 'Python was not found on PATH.' }
    } elseif (-not (Test-Path $entry)) {
        throw "Required local runtime path is missing for profile '$Profile': $entry"
    }
}

python research/authoritative/v2.1.1/scripts/validate_research_package.py
python src/north_garden/validate_production_records.py
Write-Host "Bootstrap validation passed for '$Profile'. No model download or provider call was made."

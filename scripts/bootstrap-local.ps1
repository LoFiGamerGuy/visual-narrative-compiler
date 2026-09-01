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

$manifest = Get-Content -Raw $template | ConvertFrom-Json
$profileSpec = $manifest.profiles.$Profile
if (-not $profileSpec) { throw "Runtime manifest has no profile '$Profile'." }
foreach ($requirement in $profileSpec.requirements) {
    if ($requirement.kind -eq 'executable') {
        if (-not (Get-Command $requirement.name -ErrorAction SilentlyContinue)) {
            throw "Required executable is missing for profile '$Profile': $($requirement.name)"
        }
    } elseif ($requirement.kind -eq 'directory') {
        $resolved = Join-Path $Root $requirement.path
        if (-not (Test-Path -LiteralPath $resolved -PathType Container)) {
            throw "Required local runtime directory is missing for profile '$Profile': $($requirement.path)"
        }
    } elseif ($requirement.kind -eq 'executable_or_env_path') {
        $command = Get-Command $requirement.name -ErrorAction SilentlyContinue
        $configured = [Environment]::GetEnvironmentVariable($requirement.environment)
        if (-not $command -and (-not $configured -or -not (Test-Path -LiteralPath $configured -PathType Leaf))) {
            throw "Required executable is missing for profile '$Profile': $($requirement.name); configure $($requirement.environment) with an exact local executable path."
        }
    } elseif ($requirement.kind -eq 'python_module') {
        python -c "import importlib; importlib.import_module('$($requirement.name)')"
        if ($LASTEXITCODE -ne 0) {
            throw "Required Python module is missing for profile '$Profile': $($requirement.name) (distribution $($requirement.distribution))"
        }
    } else {
        throw "Unknown runtime requirement kind: $($requirement.kind)"
    }
}

python src/north_garden/validate_runtime_asset_manifest.py --manifest $template
if ($LASTEXITCODE -ne 0) { throw 'Runtime asset example manifest validation failed.' }
if (Test-Path -LiteralPath $local) {
    python src/north_garden/validate_runtime_asset_manifest.py --manifest $local
    if ($LASTEXITCODE -ne 0) { throw 'Local runtime asset manifest validation failed.' }
}
python research/authoritative/v2.1.1/scripts/validate_research_package.py
if ($LASTEXITCODE -ne 0) { throw 'Frozen research package validation failed.' }
python src/north_garden/validate_production_records.py
if ($LASTEXITCODE -ne 0) { throw 'Production record validation failed.' }
Write-Host "Bootstrap validation passed for '$Profile'. No model download or provider call was made."

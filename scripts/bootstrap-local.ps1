param(
    [ValidateSet('documentation', 'instrumentation', 'baseline_legacy', 'blender_stage')]
    [string]$Profile = 'documentation',
    [switch]$WriteLocalRuntimeTemplate,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not $DryRun -and -not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
    Write-Host 'Created .env from .env.example; fill credentials only if you choose to run an external adapter.'
}

$template = 'config/runtime-assets.example.json'
$local = 'config/runtime-assets.local.json'
if (-not $DryRun -and $WriteLocalRuntimeTemplate -and -not (Test-Path $local)) {
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
        if ($requirement.version -and $requirement.name -eq 'python') {
            python -c "import platform; assert platform.python_version() == '$($requirement.version)', platform.python_version()"
            if ($LASTEXITCODE -ne 0) { throw "Python version mismatch for profile '$Profile': expected $($requirement.version)" }
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
        if ($requirement.version) {
            python -c "import importlib.metadata; assert importlib.metadata.version('$($requirement.distribution)') == '$($requirement.version)', importlib.metadata.version('$($requirement.distribution)')"
            if ($LASTEXITCODE -ne 0) { throw "Python distribution version mismatch for profile '$Profile': $($requirement.distribution) expected $($requirement.version)" }
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
if ($Profile -eq 'instrumentation') {
    python src/north_garden/validate_instrumentation_runtime.py
    if ($LASTEXITCODE -ne 0) { throw 'Instrumentation runtime inventory validation failed.' }
    python $profileSpec.entrypoint
    if ($LASTEXITCODE -ne 0) { throw 'Complete instrumentation suite failed.' }
}
Write-Host "Bootstrap validation passed for '$Profile'. No model download or provider call was made."

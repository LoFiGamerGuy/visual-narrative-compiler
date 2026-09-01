$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$allowed = @('.env.example', '.gitignore', 'AGENT_FIRST_PROMPT.md', 'BUNDLE_PROVENANCE.json', 'GAP_ANALYSIS.md', 'GOAL.md', 'MANIFEST.sha256', 'README_CODEX_BOOTSTRAP.md', 'VALIDATION_AT_PACKAGING.txt', 'config', 'docs', 'manifests', 'production', 'research', 'scripts', 'src')
$staged = git diff --cached --name-only
if (-not $staged) { throw 'No files are staged; stage the reviewed allowlist first.' }
foreach ($path in $staged) {
    $ok = $false
    foreach ($rootPath in $allowed) {
        if ($path -eq $rootPath -or $path.StartsWith("$rootPath/")) { $ok = $true; break }
    }
    if (-not $ok) { throw "Out-of-scope staged path: $path" }
    if ($path -match '(^|/)(\.env|.*\.(safetensors|ckpt|pt|pth|onnx|gguf|zip|tgz|log|err|out))$') { throw "Sensitive or heavyweight staged extension: $path" }
}
$whitespace = git diff --cached --check 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Warning 'The imported workspace contains pre-existing whitespace diagnostics. They are reported but do not broaden the staged scope or rewrite frozen/historical artifacts.'
    $whitespace | Select-Object -First 20 | ForEach-Object { Write-Warning $_ }
}
Write-Host "Git scope preflight passed for $($staged.Count) reviewed source/evidence files."

param(
    [string]$Python = "",
    [string]$OutDir = "outputs/v50_pc_validation_bundle",
    [string]$BundleName = "biogpu_v50_pc_validation_bundle.zip"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Push-Location $ProjectRoot
try {
    if (-not $Python) {
        if ($env:VIRTUAL_ENV) {
            $candidate = Join-Path $env:VIRTUAL_ENV "Scripts/python.exe"
            if (Test-Path $candidate) { $Python = $candidate }
        }
        if (-not $Python) { $Python = "python" }
    }

    $env:PYTHONPATH = "."
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

    & $Python -m biogpu.release.pc_validation_bundle_v50 `
        --project-root . `
        --out-dir $OutDir `
        --bundle-name $BundleName
    if ($LASTEXITCODE -ne 0) {
        throw "v5.0 PC validation bundle packaging failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
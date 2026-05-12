param(
    [string]$Python = "",
    [string]$DatasetZip = "",
    [string]$DatasetDir = "Pre_processed_MEA_data",
    [string]$OutDir = "outputs/v50_dataset_asset_validation"
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
    $arguments = @(
        "-m", "biogpu.benchmarks.biogpu_v46_clean_release",
        "--project-root", ".",
        "--dataset-dir", $DatasetDir,
        "--out-dir", $OutDir
    )

    if ($DatasetZip) {
        $arguments += @("--dataset-zip", $DatasetZip)
    }

    & $Python @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Dataset asset validation failed with exit code $LASTEXITCODE"
    }

    Write-Host "Dataset asset validation OK: $OutDir/v46_clean_release_summary.json"
}
finally {
    Pop-Location
}

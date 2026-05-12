<#
.SYNOPSIS
    BioGPU-Core v5.6 raw HDF5 structure/event inspection runner.
#>
param(
    [string]$Python = "python",
    [string]$Root = "data/external/raw_hdf5",
    [string]$OutDir = "outputs/v56_raw_hdf5_structure"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.6  Raw HDF5 Structure" -ForegroundColor Cyan
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host "Python : $Python"
    Write-Host "Root   : $Root"
    Write-Host "OutDir : $OutDir"
    Write-Host ""

    Write-Host "--- Running v56 raw HDF5 structure/event probe ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v56_raw_hdf5_structure --root $Root --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v56 raw HDF5 structure probe failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V56_RAW_HDF5_STRUCTURE_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- Probe summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status        : $($summary.overall_status)"
        Write-Host "file_count            : $($summary.file_count)"
        Write-Host "files_with_events     : $($summary.files_with_events)"
        Write-Host "event_candidate_count : $($summary.event_candidate_count)"
        Write-Host "event_total_count     : $($summary.event_total_count)"
    }

    Write-Host ""
    Write-Host "--- Running v56 raw HDF5 structure tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v56_raw_hdf5_structure.py
    if ($LASTEXITCODE -ne 0) { throw "v56 raw HDF5 structure tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host " v56 Raw HDF5 Structure PASSED" -ForegroundColor Green
    Write-Host "======================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

<#
.SYNOPSIS
    BioGPU-Core v5.15 DANDI/NWB task validation runner.
#>
param(
    [string]$Python = "python",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v515_dandi_nwb_task_validation"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.15  DANDI/NWB Task Validation" -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "Python: $Python"
    Write-Host "Root  : $Root"
    Write-Host "OutDir: $OutDir"
    Write-Host ""

    Write-Host "--- Running v515 DANDI/NWB task validation ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v515_dandi_nwb_task_validation --root $Root --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v515 DANDI/NWB task validation failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V515_DANDI_NWB_TASK_VALIDATION_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- DANDI/NWB task validation summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status  : $($summary.overall_status)"
        Write-Host "nwb_samples     : $($summary.validated_sample_count)/$($summary.nwb_sample_count)"
        Write-Host "total_units     : $($summary.total_unit_count)"
        Write-Host "total_spike_times: $($summary.total_spike_times_count)"
        Write-Host "total_windows   : $($summary.total_exported_window_count)"
    }

    Write-Host ""
    Write-Host "--- Running v515 DANDI/NWB task validation tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v515_dandi_nwb_task_validation.py
    if ($LASTEXITCODE -ne 0) { throw "v515 DANDI/NWB tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host " v515 DANDI/NWB Task Validation PASSED" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

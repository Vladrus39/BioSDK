<#
.SYNOPSIS
    BioGPU-Core v5.20 Allen orientation benchmark runner.
#>
param(
    [string]$Python = "python",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v520_allen_orientation_benchmark",
    [int]$TopUnits = 64,
    [int]$MaxWindows = 800,
    [int]$LabelShuffles = 100
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.20  Allen Orientation Benchmark" -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "Python       : $Python"
    Write-Host "Root         : $Root"
    Write-Host "OutDir       : $OutDir"
    Write-Host "TopUnits     : $TopUnits"
    Write-Host "MaxWindows   : $MaxWindows"
    Write-Host "LabelShuffles: $LabelShuffles"
    Write-Host ""

    Write-Host "--- Running v520 Allen orientation benchmark ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v520_allen_orientation_benchmark --root $Root --out-dir $OutDir --top-units $TopUnits --max-windows $MaxWindows --label-shuffles $LabelShuffles
    if ($LASTEXITCODE -ne 0) { throw "v520 Allen orientation benchmark failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V520_ALLEN_ORIENTATION_BENCHMARK_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- Allen orientation benchmark summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status     : $($summary.overall_status)"
        Write-Host "sample_count       : $($summary.sample_count)"
        Write-Host "selected_unit_count: $($summary.selected_unit_count)"
        Write-Host "feature_count      : $($summary.feature_count)"
        Write-Host "readout_status     : $($summary.readout_status)"
        Write-Host "bic_os_phase_locked: $($summary.bic_os_phase_locked)"
    }

    Write-Host ""
    Write-Host "--- Running v520 Allen orientation tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v520_allen_orientation_benchmark.py
    if ($LASTEXITCODE -ne 0) { throw "v520 Allen orientation tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host " v520 Allen Orientation Benchmark PASSED" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

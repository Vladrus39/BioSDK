<#
.SYNOPSIS
    BioGPU-Core v5.16 DANDI/NWB SDK task benchmark runner.
#>
param(
    [string]$Python = "python",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v516_dandi_nwb_task_benchmark",
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
    Write-Host " BioGPU-Core v5.16  DANDI/NWB Task Benchmark" -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "Python       : $Python"
    Write-Host "Root         : $Root"
    Write-Host "OutDir       : $OutDir"
    Write-Host "LabelShuffles: $LabelShuffles"
    Write-Host ""

    Write-Host "--- Running v516 DANDI/NWB task benchmark ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v516_dandi_nwb_task_benchmark --root $Root --out-dir $OutDir --label-shuffles $LabelShuffles
    if ($LASTEXITCODE -ne 0) { throw "v516 DANDI/NWB task benchmark failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V516_DANDI_NWB_TASK_BENCHMARK_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- DANDI/NWB task benchmark summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status            : $($summary.overall_status)"
        Write-Host "sample_count              : $($summary.sample_count)"
        Write-Host "unit_count                : $($summary.unit_count)"
        Write-Host "feature_count             : $($summary.feature_count)"
        Write-Host "observed_balanced_accuracy: $($summary.observed.balanced_accuracy)"
        Write-Host "shuffle_p_value           : $($summary.label_shuffle_baseline.p_value_balanced_accuracy_gt_shuffle)"
    }

    Write-Host ""
    Write-Host "--- Running v516 DANDI/NWB task benchmark tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v516_dandi_nwb_task_benchmark.py
    if ($LASTEXITCODE -ne 0) { throw "v516 DANDI/NWB benchmark tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host " v516 DANDI/NWB Task Benchmark PASSED" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

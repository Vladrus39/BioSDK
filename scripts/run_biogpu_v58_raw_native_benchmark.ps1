<#
.SYNOPSIS
    BioGPU-Core v5.8 raw-native HDF5 event-window benchmark runner.
#>
param(
    [string]$Python = "python",
    [string]$RawRoot = "data/external/raw_hdf5",
    [string]$RawEventCsv = "outputs/v56_raw_hdf5_structure/V56_TTL_EVENT_CANDIDATES.csv",
    [string]$V56OutDir = "outputs/v56_raw_hdf5_structure",
    [string]$OutDir = "outputs/v58_raw_native_benchmark",
    [int]$MaxEventsPerRecording = 16,
    [double]$WindowPreMs = 20.0,
    [double]$WindowPostMs = 80.0,
    [int]$LabelShuffles = 25
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.8  Raw-Native Benchmark" -ForegroundColor Cyan
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host "Python               : $Python"
    Write-Host "RawRoot              : $RawRoot"
    Write-Host "RawEventCsv          : $RawEventCsv"
    Write-Host "OutDir               : $OutDir"
    Write-Host "MaxEventsPerRecording: $MaxEventsPerRecording"
    Write-Host "Window               : -$WindowPreMs ms / +$WindowPostMs ms"
    Write-Host ""

    Write-Host "--- Running v58 raw-native benchmark ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v58_raw_native_benchmark --raw-root $RawRoot --raw-event-csv $RawEventCsv --v56-out-dir $V56OutDir --out-dir $OutDir --max-events-per-recording $MaxEventsPerRecording --window-pre-ms $WindowPreMs --window-post-ms $WindowPostMs --label-shuffles $LabelShuffles
    if ($LASTEXITCODE -ne 0) { throw "v58 raw-native benchmark failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V58_RAW_NATIVE_FEATURE_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- Benchmark summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status            : $($summary.overall_status)"
        Write-Host "raw_event_source_count    : $($summary.raw_event_source_count)"
        Write-Host "feature_row_count         : $($summary.feature_row_count)"
        Write-Host "feature_count             : $($summary.feature_count)"
        Write-Host "condition_readout_status  : $($summary.condition_readout_status)"
    }

    Write-Host ""
    Write-Host "--- Running v58 raw-native tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v58_raw_native_benchmark.py
    if ($LASTEXITCODE -ne 0) { throw "v58 raw-native benchmark tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host " v58 Raw-Native Benchmark PASSED" -ForegroundColor Green
    Write-Host "======================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

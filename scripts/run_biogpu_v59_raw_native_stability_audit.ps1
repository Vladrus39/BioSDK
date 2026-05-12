<#
.SYNOPSIS
    BioGPU-Core v5.9 raw-native stability and target coverage audit runner.
#>
param(
    [string]$Python = "python",
    [string]$MatrixNpz = "outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_FEATURE_MATRIX.npz",
    [string]$MetadataCsv = "outputs/v58_raw_native_benchmark/V58_RAW_NATIVE_EVENT_METADATA.csv",
    [string]$OutDir = "outputs/v59_raw_native_stability_audit",
    [int]$MinGroupsPerTarget = 2,
    [int]$LabelShuffles = 200,
    [int]$Seed = 59
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.9  Raw-Native Stability Audit" -ForegroundColor Cyan
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host "Python             : $Python"
    Write-Host "MatrixNpz          : $MatrixNpz"
    Write-Host "MetadataCsv        : $MetadataCsv"
    Write-Host "OutDir             : $OutDir"
    Write-Host "MinGroupsPerTarget : $MinGroupsPerTarget"
    Write-Host "LabelShuffles      : $LabelShuffles"
    Write-Host ""

    Write-Host "--- Running v59 raw-native stability audit ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v59_raw_native_stability_audit --matrix-npz $MatrixNpz --metadata-csv $MetadataCsv --out-dir $OutDir --min-groups-per-target $MinGroupsPerTarget --label-shuffles $LabelShuffles --seed $Seed
    if ($LASTEXITCODE -ne 0) { throw "v59 raw-native stability audit failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V59_RAW_NATIVE_STABILITY_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- Audit summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status                  : $($summary.overall_status)"
        Write-Host "feature_row_count               : $($summary.feature_row_count)"
        Write-Host "recording_group_count           : $($summary.recording_group_count)"
        Write-Host "split_half_cosine_median        : $($summary.split_half_cosine_median)"
        Write-Host "target_readout_signal_status    : $($summary.target_readout_signal_status)"
        Write-Host "target_fingerprint_signal_status: $($summary.target_fingerprint_signal_status)"
    }

    Write-Host ""
    Write-Host "--- Running v59 raw-native stability tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v59_raw_native_stability_audit.py
    if ($LASTEXITCODE -ne 0) { throw "v59 raw-native stability tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host " v59 Raw-Native Stability Audit PASSED" -ForegroundColor Green
    Write-Host "======================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

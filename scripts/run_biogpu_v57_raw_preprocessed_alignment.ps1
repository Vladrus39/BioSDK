<#
.SYNOPSIS
    BioGPU-Core v5.7 raw-vs-preprocessed alignment audit runner.
#>
param(
    [string]$Python = "python",
    [string]$RawEventCsv = "outputs/v56_raw_hdf5_structure/V56_TTL_EVENT_CANDIDATES.csv",
    [string]$PulseMetadataCsv = "evidence/outputs/realdata_zenodo_14363732_v15_readout/pulse_feature_metadata.csv",
    [string]$RawRoot = "data/external/raw_hdf5",
    [string]$V56OutDir = "outputs/v56_raw_hdf5_structure",
    [string]$OutDir = "outputs/v57_raw_preprocessed_alignment"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.7  Raw vs Preprocessed Alignment" -ForegroundColor Cyan
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host "Python          : $Python"
    Write-Host "RawEventCsv     : $RawEventCsv"
    Write-Host "PulseMetadataCsv: $PulseMetadataCsv"
    Write-Host "OutDir          : $OutDir"
    Write-Host ""

    Write-Host "--- Running v57 raw-vs-preprocessed alignment audit ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v57_raw_preprocessed_alignment --raw-event-csv $RawEventCsv --pulse-metadata-csv $PulseMetadataCsv --raw-root $RawRoot --v56-out-dir $V56OutDir --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v57 raw-vs-preprocessed alignment audit failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V57_RAW_PREPROCESSED_ALIGNMENT_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- Audit summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status                 : $($summary.overall_status)"
        Write-Host "raw_event_recording_count      : $($summary.raw_event_recording_count)"
        Write-Host "preprocessed_pulse_recordings  : $($summary.preprocessed_pulse_recording_count)"
        Write-Host "exact_recording_match_count    : $($summary.exact_recording_match_count)"
        Write-Host "condition_target_match_count   : $($summary.condition_target_match_count)"
        Write-Host "temporal_signature_match_count : $($summary.temporal_signature_match_count)"
    }

    Write-Host ""
    Write-Host "--- Running v57 alignment tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v57_raw_preprocessed_alignment.py
    if ($LASTEXITCODE -ne 0) { throw "v57 raw-vs-preprocessed alignment tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host " v57 Raw vs Preprocessed Alignment PASSED" -ForegroundColor Green
    Write-Host "======================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

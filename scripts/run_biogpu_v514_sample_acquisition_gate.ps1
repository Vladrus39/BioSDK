<#
.SYNOPSIS
    BioGPU-Core v5.14 BioSDK sample acquisition gate runner.
#>
param(
    [string]$Python = "python",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v514_sample_acquisition_gate"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.14  Sample Acquisition Gate" -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "Python: $Python"
    Write-Host "Root  : $Root"
    Write-Host "OutDir: $OutDir"
    Write-Host ""

    Write-Host "--- Running v514 sample acquisition gate ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v514_sample_acquisition_gate --root $Root --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v514 sample acquisition gate failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V514_SAMPLE_ACQUISITION_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- Sample acquisition summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status     : $($summary.overall_status)"
        Write-Host "active_phase       : $($summary.active_phase)"
        Write-Host "bic_os_phase_locked: $($summary.bic_os_phase_locked)"
        Write-Host "local_sources      : $($summary.locally_available_independent_source_count)/$($summary.independent_source_target)"
        Write-Host "dandi_nwb_validated: $($summary.dandi_nwb_validated)"
    }

    Write-Host ""
    Write-Host "--- Running v514 sample acquisition tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v514_sample_acquisition_gate.py
    if ($LASTEXITCODE -ne 0) { throw "v514 sample acquisition tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host " v514 Sample Acquisition Gate PASSED" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

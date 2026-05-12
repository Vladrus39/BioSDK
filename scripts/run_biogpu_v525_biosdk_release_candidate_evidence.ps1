<#
.SYNOPSIS
    BioGPU-Core v5.25 BioSDK release-candidate evidence package runner.
#>
param(
    [string]$Python = "python",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v525_biosdk_release_candidate_evidence"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.25  BioSDK RC Evidence" -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "Python: $Python"
    Write-Host "Root  : $Root"
    Write-Host "OutDir: $OutDir"
    Write-Host ""

    Write-Host "--- Running v525 BioSDK RC evidence package ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v525_biosdk_release_candidate_evidence --root $Root --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v525 BioSDK RC evidence package failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V525_BIOSDK_RELEASE_CANDIDATE_EVIDENCE_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- BioSDK RC evidence summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status        : $($summary.overall_status)"
        Write-Host "rc_evidence_ready     : $($summary.biosdk_release_candidate_evidence_ready)"
        Write-Host "ready_required_items  : $($summary.ready_required_item_count)/$($summary.required_item_count)"
        Write-Host "full_biosdk_ready     : $($summary.full_biosdk_ready)"
        Write-Host "bic_os_phase_locked   : $($summary.bic_os_phase_locked)"
    }

    Write-Host ""
    Write-Host "--- Running v525 tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v525_biosdk_release_candidate_evidence.py
    if ($LASTEXITCODE -ne 0) { throw "v525 tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host " v5.25 BioSDK RC Evidence PASSED" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
} finally {
    Pop-Location
}
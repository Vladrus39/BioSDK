<#
.SYNOPSIS
    BioGPU-Core v5.3 evidence ledger runner.

.DESCRIPTION
    Builds a reference v24 result bundle, validates known evidence bundles,
    creates a chained local integrity ledger, and runs focused v5.3 tests.
#>
param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v53_evidence_ledger"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.3  Evidence Ledger" -ForegroundColor Cyan
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host "Python : $Python"
    Write-Host "OutDir : $OutDir"
    Write-Host "Root   : $ProjectRoot"
    Write-Host ""

    Write-Host "--- Running v53 evidence ledger probe ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v53_evidence_ledger --project-root "." --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v53 evidence ledger probe failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V53_EVIDENCE_LEDGER_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- Probe summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "milestone             : $($summary.milestone)"
        Write-Host "audited_bundle_count  : $($summary.audited_bundle_count)"
        Write-Host "valid_bundle_count    : $($summary.valid_bundle_count)"
        Write-Host "ledger_chain_valid    : $($summary.ledger_chain_valid)"
        Write-Host "reference_bundle_valid: $($summary.reference_bundle_valid)"
    }

    Write-Host ""
    Write-Host "--- Running v53 evidence ledger tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v53_evidence_ledger.py
    if ($LASTEXITCODE -ne 0) { throw "v53 evidence ledger tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host " v53 evidence ledger PASSED" -ForegroundColor Green
    Write-Host "======================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

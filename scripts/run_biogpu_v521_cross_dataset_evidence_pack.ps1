<#
.SYNOPSIS
    BioGPU-Core v5.21 cross-dataset BioSDK evidence pack runner.
#>
param(
    [string]$Python = "python",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v521_cross_dataset_evidence_pack"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.21  Cross-Dataset Evidence Pack" -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "Python: $Python"
    Write-Host "Root  : $Root"
    Write-Host "OutDir: $OutDir"
    Write-Host ""

    Write-Host "--- Running v521 cross-dataset evidence pack ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v521_cross_dataset_evidence_pack --root $Root --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v521 cross-dataset evidence pack failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V521_CROSS_DATASET_EVIDENCE_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- Cross-dataset evidence summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status                     : $($summary.overall_status)"
        Write-Host "public_cross_dataset_evidence_ready: $($summary.public_cross_dataset_evidence_ready)"
        Write-Host "public_benchmark_sources           : $($summary.public_benchmark_source_count)/$($summary.public_source_target)"
        Write-Host "external_partner_evidence_ready    : $($summary.external_partner_evidence_ready)"
        Write-Host "vendor_user_evidence_ready         : $($summary.vendor_user_evidence_ready)"
        Write-Host "bic_os_phase_locked                : $($summary.bic_os_phase_locked)"
    }

    Write-Host ""
    Write-Host "--- Running v521 tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v521_cross_dataset_evidence_pack.py
    if ($LASTEXITCODE -ne 0) { throw "v521 tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host " v5.21 Cross-Dataset Evidence Pack PASSED" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

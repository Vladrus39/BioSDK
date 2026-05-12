<#
.SYNOPSIS
    BioGPU-Core v5.10 project alignment and claim audit runner.
#>
param(
    [string]$Python = "python",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v510_project_alignment_claim_audit"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.10  Project Alignment Claim Audit" -ForegroundColor Cyan
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host "Python: $Python"
    Write-Host "Root  : $Root"
    Write-Host "OutDir: $OutDir"
    Write-Host ""

    Write-Host "--- Running v510 project alignment claim audit ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v510_project_alignment_claim_audit --root $Root --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v510 project alignment claim audit failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V510_PROJECT_ALIGNMENT_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- Claim audit summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status                    : $($summary.overall_status)"
        Write-Host "did_we_drift_from_project_meaning : $($summary.direct_answer.did_we_drift_from_project_meaning)"
        Write-Host "is_global_uniqueness_proven       : $($summary.direct_answer.is_the_code_globally_unique_proven)"
    }

    Write-Host ""
    Write-Host "--- Running v510 project alignment tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v510_project_alignment_claim_audit.py
    if ($LASTEXITCODE -ne 0) { throw "v510 project alignment tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host " v510 Project Alignment Claim Audit PASSED" -ForegroundColor Green
    Write-Host "======================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

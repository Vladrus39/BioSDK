<#
.SYNOPSIS
    BioGPU-Core v5.22 BioSDK public examples runner.
#>
param(
    [string]$Python = "python",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v522_biosdk_public_examples"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.22  BioSDK Public Examples" -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "Python: $Python"
    Write-Host "Root  : $Root"
    Write-Host "OutDir: $OutDir"
    Write-Host ""

    Write-Host "--- Running v522 BioSDK public examples gate ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v522_biosdk_public_examples --root $Root --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v522 public examples gate failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V522_BIOSDK_PUBLIC_EXAMPLES_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- BioSDK public examples summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status              : $($summary.overall_status)"
        Write-Host "public_examples_ready       : $($summary.public_examples_ready)"
        Write-Host "ready_required_examples     : $($summary.ready_required_public_example_count)/$($summary.required_public_example_count)"
        Write-Host "external_partner_ready      : $($summary.external_partner_evidence_ready)"
        Write-Host "vendor_user_ready           : $($summary.vendor_user_evidence_ready)"
        Write-Host "bic_os_phase_locked         : $($summary.bic_os_phase_locked)"
    }

    Write-Host ""
    Write-Host "--- Running v522 tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v522_biosdk_public_examples.py
    if ($LASTEXITCODE -ne 0) { throw "v522 tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host " v5.22 BioSDK Public Examples PASSED" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

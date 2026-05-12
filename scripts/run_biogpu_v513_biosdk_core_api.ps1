<#
.SYNOPSIS
    BioGPU-Core v5.13 BioSDK core API runner.
#>
param(
    [string]$Python = "python",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v513_biosdk_core_api"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.13  BioSDK Core API" -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "Python: $Python"
    Write-Host "Root  : $Root"
    Write-Host "OutDir: $OutDir"
    Write-Host ""

    Write-Host "--- Running v513 BioSDK core API reference flow ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v513_biosdk_core_api --root $Root --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v513 BioSDK core API failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V513_BIOSDK_CORE_API_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- BioSDK core API summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status          : $($summary.overall_status)"
        Write-Host "active_phase            : $($summary.active_phase)"
        Write-Host "bic_os_phase_locked     : $($summary.bic_os_phase_locked)"
        Write-Host "nsi_manifest_valid      : $($summary.nsi_manifest_valid)"
        Write-Host "queue_admission_accepted: $($summary.queue_admission_accepted)"
    }

    Write-Host ""
    Write-Host "--- Running v513 BioSDK core API tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v513_biosdk_core_api.py
    if ($LASTEXITCODE -ne 0) { throw "v513 BioSDK core API tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host " v513 BioSDK Core API PASSED" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

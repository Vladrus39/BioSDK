<#
.SYNOPSIS
    BioGPU-Core v5.27 local scheduler API facade proof.
#>
param(
    [string]$Python = "python",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v527_scheduler_api_facade"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.27  Scheduler API Facade" -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "Python: $Python"
    Write-Host "Root  : $Root"
    Write-Host "OutDir: $OutDir"
    Write-Host ""

    Write-Host "--- Running v527 scheduler API facade proof ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v527_scheduler_api_facade --root $Root --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v527 scheduler API facade proof failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V527_SCHEDULER_API_FACADE_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- Scheduler API facade summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status      : $($summary.overall_status)"
        Write-Host "facade_ready        : $($summary.scheduler_api_facade_ready)"
        Write-Host "api_routes          : $($summary.api_route_count)"
        Write-Host "cancel_semantics    : $($summary.cancel_semantics_passed)"
        Write-Host "timeout_semantics   : $($summary.timeout_semantics_passed)"
        Write-Host "retry_semantics     : $($summary.retry_semantics_passed)"
        Write-Host "production_api_ready: $($summary.production_api_ready)"
        Write-Host "bic_os_phase_locked : $($summary.bic_os_phase_locked)"
    }

    Write-Host ""
    Write-Host "--- Running v527 tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v527_scheduler_api_facade.py
    if ($LASTEXITCODE -ne 0) { throw "v527 tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host " v5.27 Scheduler API Facade PASSED" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
} finally {
    Pop-Location
}
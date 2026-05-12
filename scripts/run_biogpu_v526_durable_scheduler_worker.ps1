<#
.SYNOPSIS
    BioGPU-Core v5.26 durable scheduler and local worker proof.
#>
param(
    [string]$Python = "python",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v526_durable_scheduler_worker"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.26  Durable Scheduler Worker" -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "Python: $Python"
    Write-Host "Root  : $Root"
    Write-Host "OutDir: $OutDir"
    Write-Host ""

    Write-Host "--- Running v526 durable scheduler worker proof ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v526_durable_scheduler_worker --root $Root --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v526 durable scheduler worker proof failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V526_DURABLE_SCHEDULER_WORKER_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- Durable scheduler summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status        : $($summary.overall_status)"
        Write-Host "proof_ready           : $($summary.durable_scheduler_worker_proof_ready)"
        Write-Host "persisted_jobs        : $($summary.persisted_job_count)"
        Write-Host "succeeded_jobs        : $($summary.succeeded_job_count)"
        Write-Host "production_ready      : $($summary.production_scheduler_ready)"
        Write-Host "bic_os_phase_locked   : $($summary.bic_os_phase_locked)"
    }

    Write-Host ""
    Write-Host "--- Running v526 tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v526_durable_scheduler_worker.py
    if ($LASTEXITCODE -ne 0) { throw "v526 tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host " v5.26 Durable Scheduler Worker PASSED" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
} finally {
    Pop-Location
}
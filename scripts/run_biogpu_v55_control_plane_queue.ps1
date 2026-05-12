<#
.SYNOPSIS
    BioGPU-Core v5.5 Control Plane Queue Bridge runner.

.DESCRIPTION
    Runs the offline bridge from v5.4 approved agent manifests into the v4.3 hosted queue model, then runs focused tests.
#>
param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v55_control_plane_queue"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.5  Control Plane Queue Bridge" -ForegroundColor Cyan
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host "Python : $Python"
    Write-Host "OutDir : $OutDir"
    Write-Host "Root   : $ProjectRoot"
    Write-Host ""

    Write-Host "--- Running v55 Control Plane Queue probe ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v55_control_plane_queue --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v55 Control Plane Queue probe failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V55_CONTROL_PLANE_QUEUE_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- Probe summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "version                       : $($summary.version)"
        Write-Host "queued_job_count              : $($summary.queued_job_count)"
        Write-Host "safe_replay_admitted          : $($summary.safe_replay_admitted)"
        Write-Host "blocked_actuation_rejected    : $($summary.blocked_actuation_rejected)"
    }

    Write-Host ""
    Write-Host "--- Running v55 Control Plane Queue tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v55_control_plane_queue.py
    if ($LASTEXITCODE -ne 0) { throw "v55 Control Plane Queue tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host " v55 Control Plane Queue Bridge PASSED" -ForegroundColor Green
    Write-Host "======================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

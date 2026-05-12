<#
.SYNOPSIS
    BioGPU-Core v5.19 vendor/user-upload read-only sample gate runner.
#>
param(
    [string]$Python = "python",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v519_vendor_user_upload_gate"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.19  Vendor/User Upload Gate" -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "Python: $Python"
    Write-Host "Root  : $Root"
    Write-Host "OutDir: $OutDir"
    Write-Host ""

    Write-Host "--- Running v519 vendor/user-upload gate ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v519_vendor_user_upload_gate --root $Root --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v519 vendor/user-upload gate failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V519_VENDOR_USER_UPLOAD_GATE_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- Vendor/user-upload summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status     : $($summary.overall_status)"
        Write-Host "samples            : $($summary.sample_count)"
        Write-Host "validated_samples  : $($summary.validated_sample_count)"
        Write-Host "blocked_samples    : $($summary.blocked_sample_count)"
        Write-Host "bic_os_phase_locked: $($summary.bic_os_phase_locked)"
    }

    Write-Host ""
    Write-Host "--- Running v519 vendor/user-upload tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v519_vendor_user_upload_gate.py
    if ($LASTEXITCODE -ne 0) { throw "v519 vendor/user-upload tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host " v519 Vendor/User Upload Gate PASSED" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

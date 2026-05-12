<#
.SYNOPSIS
    BioGPU-Core v5.11 BiC OS boot readiness runner.
#>
param(
    [string]$Python = "python",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v511_bic_os_boot_readiness"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.11  BiC OS Boot Readiness" -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "Python: $Python"
    Write-Host "Root  : $Root"
    Write-Host "OutDir: $OutDir"
    Write-Host ""

    Write-Host "--- Running v511 BiC OS boot readiness audit ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v511_bic_os_boot_readiness --root $Root --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v511 BiC OS boot readiness failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V511_BIC_OS_BOOT_READINESS_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- BiC OS boot readiness summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "product_name                    : $($summary.product_name)"
        Write-Host "overall_status                  : $($summary.overall_status)"
        Write-Host "offline_runtime_kernel_bootable : $($summary.offline_runtime_kernel_bootable)"
        Write-Host "production_os_ready             : $($summary.production_os_ready)"
        Write-Host "production_blocker_count        : $($summary.production_blocker_count)"
    }

    Write-Host ""
    Write-Host "--- Running v511 BiC OS boot readiness tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v511_bic_os_boot_readiness.py
    if ($LASTEXITCODE -ne 0) { throw "v511 BiC OS boot readiness tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host " v511 BiC OS Boot Readiness PASSED" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

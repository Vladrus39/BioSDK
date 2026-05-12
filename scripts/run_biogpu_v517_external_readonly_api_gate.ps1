<#
.SYNOPSIS
    BioGPU-Core v5.17 external read-only API/export gate runner.
#>
param(
    [string]$Python = "python",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v517_external_readonly_api_gate"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.17  External Read-Only API Gate" -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "Python: $Python"
    Write-Host "Root  : $Root"
    Write-Host "OutDir: $OutDir"
    Write-Host ""

    Write-Host "--- Running v517 external read-only API gate ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v517_external_readonly_api_gate --root $Root --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v517 external read-only API gate failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V517_EXTERNAL_READONLY_API_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- External read-only API summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status       : $($summary.overall_status)"
        Write-Host "mock_contracts       : $($summary.mock_contract_passed_count)/$($summary.platform_count)"
        Write-Host "real_external_ready  : $($summary.real_external_ready)"
        Write-Host "real_export_file_count: $($summary.real_export_file_count)"
        Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"
    }

    Write-Host ""
    Write-Host "--- Running v517 external read-only API tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v517_external_readonly_api_gate.py
    if ($LASTEXITCODE -ne 0) { throw "v517 external read-only API tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host " v517 External Read-Only API Gate PASSED" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

<#
.SYNOPSIS
    BioGPU-Core v5.24 external read-only export validation workflow.
#>
param(
    [string]$Python = "python",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v524_external_export_validation"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.24  External Export Validation" -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "Python: $Python"
    Write-Host "Root  : $Root"
    Write-Host "OutDir: $OutDir"
    Write-Host ""

    Write-Host "--- Running v524 external export validation ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v524_external_export_validation --root $Root --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v524 external export validation failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V524_EXTERNAL_EXPORT_VALIDATION_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- External export validation summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status          : $($summary.overall_status)"
        Write-Host "candidate_export_count  : $($summary.candidate_export_count)"
        Write-Host "validated_export_count  : $($summary.validated_export_count)"
        Write-Host "real_external_ready     : $($summary.real_external_ready)"
        Write-Host "bic_os_phase_locked     : $($summary.bic_os_phase_locked)"
    }

    Write-Host ""
    Write-Host "--- Running v524 tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v524_external_export_validation.py tests/current/test_biogpu_v517_external_readonly_api_gate.py
    if ($LASTEXITCODE -ne 0) { throw "v524 tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host " v5.24 External Export Validation PASSED" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
} finally {
    Pop-Location
}
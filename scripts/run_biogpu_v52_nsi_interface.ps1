<#
.SYNOPSIS
    BioGPU-Core v5.2 NSI/interface runner.

.DESCRIPTION
    Runs the NSI-1.0 frozen schema probe, adapter conformance checks,
    reference result-bundle validation, and focused v5.2 tests.

.PARAMETER Python
    Python interpreter path. Defaults to python.

.PARAMETER OutDir
    Output directory for NSI artifacts.
#>
param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v52_nsi_interface"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.2  NSI Interface Phase" -ForegroundColor Cyan
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host "Python : $Python"
    Write-Host "OutDir : $OutDir"
    Write-Host "Root   : $ProjectRoot"
    Write-Host ""

    Write-Host "--- Running v52 NSI/interface probe ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v52_nsi_interface --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v52 NSI/interface probe failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "--- Running validate-nsi CLI smoke ---" -ForegroundColor Yellow
    & $Python -m biogpu.standards.nsi_cli_v52 --list-schemas | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "validate-nsi CLI smoke failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V52_NSI_INTERFACE_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- Probe summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "milestone                : $($summary.milestone)"
        Write-Host "schema_status            : $($summary.schema_status)"
        Write-Host "schema_count             : $($summary.schema_count)"
        Write-Host "reference_objects_valid  : $($summary.reference_objects_valid)"
        Write-Host "result_bundle_valid      : $($summary.result_bundle_valid)"
        Write-Host "adapter_conformance_pass : $($summary.gate.adapter_conformance_passed)"
    }

    Write-Host ""
    Write-Host "--- Running v52 NSI/interface tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q `
        tests/current/test_biogpu_v52_nsi_interface.py `
        tests/current/test_biogpu_v52_validate_nsi_cli.py
    if ($LASTEXITCODE -ne 0) { throw "v52 NSI/interface tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host " v52 NSI/interface phase PASSED" -ForegroundColor Green
    Write-Host "======================================================" -ForegroundColor Green
} finally {
    Pop-Location
}
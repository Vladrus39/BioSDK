<#
.SYNOPSIS
    BioGPU-Core v5.18 Allen visual-coding orientation sample gate runner.
#>
param(
    [string]$Python = "python",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v518_allen_orientation_gate"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.18  Allen Orientation Gate" -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "Python: $Python"
    Write-Host "Root  : $Root"
    Write-Host "OutDir: $OutDir"
    Write-Host ""

    Write-Host "--- Running v518 Allen orientation gate ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v518_allen_orientation_gate --root $Root --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v518 Allen orientation gate failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V518_ALLEN_ORIENTATION_GATE_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- Allen orientation summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status    : $($summary.overall_status)"
        Write-Host "nwb_samples       : $($summary.nwb_sample_count)"
        Write-Host "manifest_assets   : $($summary.manifest_asset_count)"
        Write-Host "validated_samples : $($summary.validated_sample_count)"
        Write-Host "bic_os_phase_locked: $($summary.bic_os_phase_locked)"
    }

    Write-Host ""
    Write-Host "--- Running v518 Allen orientation tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v518_allen_orientation_gate.py
    if ($LASTEXITCODE -ne 0) { throw "v518 Allen orientation tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host " v518 Allen Orientation Gate PASSED" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

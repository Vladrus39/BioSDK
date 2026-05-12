<#
.SYNOPSIS
    BioGPU-Core v5.23 safe user-upload fixture workflow.
#>
param(
    [string]$Python = "python",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v523_user_upload_fixture",
    [switch]$NoOverwrite
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.23  Safe User-Upload Fixture" -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "Python: $Python"
    Write-Host "Root  : $Root"
    Write-Host "OutDir: $OutDir"
    Write-Host ""

    Write-Host "--- Running v523 safe user-upload workflow ---" -ForegroundColor Yellow
    $args = @("-m", "biogpu.benchmarks.biogpu_v523_user_upload_fixture", "--root", $Root, "--out-dir", $OutDir)
    if ($NoOverwrite) { $args += "--no-overwrite" }
    & $Python @args
    if ($LASTEXITCODE -ne 0) { throw "v523 user-upload fixture workflow failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V523_USER_UPLOAD_FIXTURE_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- User-upload fixture summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "overall_status               : $($summary.overall_status)"
        Write-Host "fixture_validation_status    : $($summary.fixture_validation_status)"
        Write-Host "user_upload_validated        : $($summary.user_upload_validated)"
        Write-Host "vendor_export_validated      : $($summary.vendor_export_validated)"
        Write-Host "external_partner_ready       : $($summary.external_partner_evidence_ready)"
        Write-Host "full_sample_proof_ready      : $($summary.full_sample_proof_ready)"
        Write-Host "bic_os_phase_locked          : $($summary.bic_os_phase_locked)"
    }

    Write-Host ""
    Write-Host "--- Running v523 tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v523_user_upload_fixture.py
    if ($LASTEXITCODE -ne 0) { throw "v523 tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host " v5.23 Safe User-Upload Fixture PASSED" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

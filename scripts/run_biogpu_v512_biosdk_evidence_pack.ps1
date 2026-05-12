<#
.SYNOPSIS
    BioGPU-Core v5.12 BioSDK evidence pack runner.
#>
param(
    [string]$Python = "python",
    [string]$Root = ".",
    [string]$OutDir = "outputs/v512_biosdk_evidence_pack"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.12  BioSDK Evidence Pack" -ForegroundColor Cyan
    Write-Host "=====================================================" -ForegroundColor Cyan
    Write-Host "Python: $Python"
    Write-Host "Root  : $Root"
    Write-Host "OutDir: $OutDir"
    Write-Host ""

    Write-Host "--- Running v512 BioSDK evidence pack audit ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v512_biosdk_evidence_pack --root $Root --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v512 BioSDK evidence pack failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V512_BIOSDK_EVIDENCE_PACK_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- BioSDK evidence pack summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "sdk_name                      : $($summary.sdk_name)"
        Write-Host "overall_status                : $($summary.overall_status)"
        Write-Host "biosdk_evidence_kernel_ready  : $($summary.biosdk_evidence_kernel_ready)"
        Write-Host "full_biosdk_ready             : $($summary.full_biosdk_ready)"
        Write-Host "locally_proven_capabilities   : $($summary.locally_proven_capability_count)/$($summary.capability_count)"
    }

    Write-Host ""
    Write-Host "--- Running v512 BioSDK evidence pack tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v512_biosdk_evidence_pack.py
    if ($LASTEXITCODE -ne 0) { throw "v512 BioSDK evidence pack tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "=====================================================" -ForegroundColor Green
    Write-Host " v512 BioSDK Evidence Pack PASSED" -ForegroundColor Green
    Write-Host "=====================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

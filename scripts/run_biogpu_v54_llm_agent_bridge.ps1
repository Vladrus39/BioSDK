<#
.SYNOPSIS
    BioGPU-Core v5.4 LLM/Agent Bridge runner.

.DESCRIPTION
    Runs the safe LLM/agent task bridge probe and focused tests.
#>
param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v54_llm_agent_bridge"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = "."

    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host " BioGPU-Core v5.4  LLM/Agent Bridge" -ForegroundColor Cyan
    Write-Host "======================================================" -ForegroundColor Cyan
    Write-Host "Python : $Python"
    Write-Host "OutDir : $OutDir"
    Write-Host "Root   : $ProjectRoot"
    Write-Host ""

    Write-Host "--- Running v54 LLM/Agent Bridge probe ---" -ForegroundColor Yellow
    & $Python -m biogpu.benchmarks.biogpu_v54_llm_agent_bridge --out-dir $OutDir
    if ($LASTEXITCODE -ne 0) { throw "v54 LLM/Agent Bridge probe failed (exit $LASTEXITCODE)" }

    $summaryPath = Join-Path $OutDir "V54_LLM_AGENT_BRIDGE_SUMMARY.json"
    if (Test-Path $summaryPath) {
        Write-Host ""
        Write-Host "--- Probe summary ---" -ForegroundColor Yellow
        $summary = Get-Content $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
        Write-Host "milestone                    : $($summary.milestone)"
        Write-Host "tool_count                   : $($summary.tool_count)"
        Write-Host "approved_count               : $($summary.approved_count)"
        Write-Host "direct_actuation_blocked     : $($summary.gate.direct_actuation_blocked)"
    }

    Write-Host ""
    Write-Host "--- Running v54 LLM/Agent Bridge tests ---" -ForegroundColor Yellow
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
    & $Python -m pytest -q tests/current/test_biogpu_v54_llm_agent_bridge.py
    if ($LASTEXITCODE -ne 0) { throw "v54 LLM/Agent Bridge tests failed (exit $LASTEXITCODE)" }

    Write-Host ""
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host " v54 LLM/Agent Bridge PASSED" -ForegroundColor Green
    Write-Host "======================================================" -ForegroundColor Green
} finally {
    Pop-Location
}

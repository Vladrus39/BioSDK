param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v549_production_readiness_gap"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.49  Production Readiness Gap"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v549 production readiness gap proof ---"
& $Python -m biogpu.benchmarks.biogpu_v549_production_readiness_gap --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Production readiness gap summary ---"
$summaryPath = Join-Path $OutDir "V549_PRODUCTION_READINESS_GAP_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "contract_ready       : $($summary.production_readiness_gap_contract_ready)"
Write-Host "v548_dependency      : $($summary.v548_dependency_ready)"
Write-Host "gap_matrix           : $($summary.production_readiness_gap_matrix_ready)"
Write-Host "pilot_matrix         : $($summary.staged_pilot_acceptance_matrix_ready)"
Write-Host "blocker_register     : $($summary.readiness_blocker_register_ready)"
Write-Host "open_gap_count       : $($summary.open_gap_count)"
Write-Host "ready_domain_count   : $($summary.production_ready_domain_count)"
Write-Host "production_ready     : $($summary.production_ready)"
Write-Host "external_pilot_ready : $($summary.real_external_pilot_ready)"
Write-Host "full_biosdk_ready    : $($summary.full_biosdk_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.production_readiness_gap_contract_ready) {
    throw "v5.49 production readiness gap contract failed"
}
if ($summary.production_ready) {
    throw "v5.49 must not claim production readiness"
}
if ($summary.real_external_pilot_ready) {
    throw "v5.49 must not claim real external pilot readiness"
}
if ($summary.full_biosdk_ready) {
    throw "v5.49 must not claim full BioSDK readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.49 must keep BiC OS phase locked"
}
if ($summary.production_ready_domain_count -ne 0) {
    throw "v5.49 must keep every production domain blocked"
}

Write-Host ""
Write-Host "--- Running v549 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v549_production_readiness_gap.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.49 Production Readiness Gap Contract PASSED"
Write-Host "====================================================="
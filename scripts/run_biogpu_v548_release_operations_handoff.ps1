param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v548_release_operations_handoff"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.48  Release Operations Handoff"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v548 release operations handoff proof ---"
& $Python -m biogpu.benchmarks.biogpu_v548_release_operations_handoff --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Release operations handoff summary ---"
$summaryPath = Join-Path $OutDir "V548_RELEASE_OPERATIONS_HANDOFF_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "contract_ready       : $($summary.release_operations_handoff_contract_ready)"
Write-Host "v547_dependency      : $($summary.v547_dependency_ready)"
Write-Host "runbook_ready        : $($summary.release_operations_runbook_ready)"
Write-Host "handoff_matrix       : $($summary.operator_handoff_matrix_ready)"
Write-Host "handoff_packet       : $($summary.operator_handoff_packet_ready)"
Write-Host "claim_boundary       : $($summary.claim_boundary_attestation_ready)"
Write-Host "production_release   : $($summary.production_release_ready)"
Write-Host "production_ops       : $($summary.production_operations_ready)"
Write-Host "full_biosdk_ready    : $($summary.full_biosdk_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.release_operations_handoff_contract_ready) {
    throw "v5.48 release operations handoff contract failed"
}
if ($summary.production_release_ready) {
    throw "v5.48 must not claim production release readiness"
}
if ($summary.production_operations_ready) {
    throw "v5.48 must not claim production operations readiness"
}
if ($summary.full_biosdk_ready) {
    throw "v5.48 must not claim full BioSDK readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.48 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v548 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v548_release_operations_handoff.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.48 Release Operations Handoff Contract PASSED"
Write-Host "====================================================="
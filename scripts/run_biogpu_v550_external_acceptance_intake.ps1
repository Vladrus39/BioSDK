param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v550_external_acceptance_intake"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.50  External Acceptance Intake"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v550 external acceptance intake proof ---"
& $Python -m biogpu.benchmarks.biogpu_v550_external_acceptance_intake --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- External acceptance intake summary ---"
$summaryPath = Join-Path $OutDir "V550_EXTERNAL_ACCEPTANCE_INTAKE_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "contract_ready       : $($summary.external_acceptance_intake_contract_ready)"
Write-Host "v549_dependency      : $($summary.v549_dependency_ready)"
Write-Host "schema_ready         : $($summary.external_acceptance_evidence_schema_ready)"
Write-Host "matrix_ready         : $($summary.external_acceptance_evidence_matrix_ready)"
Write-Host "intake_gate          : $($summary.real_pilot_intake_gate_ready)"
Write-Host "real_acceptance      : $($summary.real_acceptance_ready_count)"
Write-Host "external_pilot_ready : $($summary.real_external_pilot_ready)"
Write-Host "production_ready     : $($summary.production_ready)"
Write-Host "full_biosdk_ready    : $($summary.full_biosdk_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.external_acceptance_intake_contract_ready) {
    throw "v5.50 external acceptance intake contract failed"
}
if ($summary.real_acceptance_ready_count -ne 0) {
    throw "v5.50 must not claim real external acceptance records"
}
if ($summary.real_external_pilot_ready) {
    throw "v5.50 must not claim real external pilot readiness"
}
if ($summary.production_ready) {
    throw "v5.50 must not claim production readiness"
}
if ($summary.full_biosdk_ready) {
    throw "v5.50 must not claim full BioSDK readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.50 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v550 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v550_external_acceptance_intake.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.50 External Acceptance Intake Contract PASSED"
Write-Host "====================================================="
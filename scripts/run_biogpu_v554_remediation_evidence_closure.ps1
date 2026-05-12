param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v554_remediation_evidence_closure"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.54  Remediation Evidence Closure"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v554 remediation evidence closure proof ---"
& $Python -m biogpu.benchmarks.biogpu_v554_remediation_evidence_closure --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Remediation evidence closure summary ---"
$summaryPath = Join-Path $OutDir "V554_REMEDIATION_EVIDENCE_CLOSURE_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "contract_ready       : $($summary.remediation_evidence_closure_contract_ready)"
Write-Host "v553_dependency      : $($summary.v553_dependency_ready)"
Write-Host "evidence_matrix      : $($summary.remediation_evidence_matrix_ready)"
Write-Host "attestation_packet   : $($summary.closure_attestation_packet_ready)"
Write-Host "closure_gate_ready   : $($summary.closure_attestation_gate_ready)"
Write-Host "real_attestations    : $($summary.real_closure_attestation_ready_count)"
Write-Host "attested_closures    : $($summary.finding_closure_attested_count)"
Write-Host "external_review_ready: $($summary.real_external_review_ready)"
Write-Host "external_pilot_ready : $($summary.real_external_pilot_ready)"
Write-Host "production_ready     : $($summary.production_ready)"
Write-Host "full_biosdk_ready    : $($summary.full_biosdk_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.remediation_evidence_closure_contract_ready) {
    throw "v5.54 remediation evidence closure contract failed"
}
if ($summary.real_closure_attestation_ready_count -ne 0) {
    throw "v5.54 must not claim real closure attestations"
}
if ($summary.finding_closure_attested_count -ne 0) {
    throw "v5.54 must not claim attested finding closures"
}
if ($summary.real_external_review_ready) {
    throw "v5.54 must not claim real external review readiness"
}
if ($summary.real_external_pilot_ready) {
    throw "v5.54 must not claim real external pilot readiness"
}
if ($summary.production_ready) {
    throw "v5.54 must not claim production readiness"
}
if ($summary.full_biosdk_ready) {
    throw "v5.54 must not claim full BioSDK readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.54 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v554 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v554_remediation_evidence_closure.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.54 Remediation Evidence Closure Contract PASSED"
Write-Host "====================================================="
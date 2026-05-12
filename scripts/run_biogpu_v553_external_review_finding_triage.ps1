param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v553_external_review_finding_triage"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.53  External Review Finding Triage"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v553 external review finding triage proof ---"
& $Python -m biogpu.benchmarks.biogpu_v553_external_review_finding_triage --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- External review finding triage summary ---"
$summaryPath = Join-Path $OutDir "V553_EXTERNAL_REVIEW_FINDING_TRIAGE_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "contract_ready       : $($summary.external_review_finding_triage_contract_ready)"
Write-Host "v552_dependency      : $($summary.v552_dependency_ready)"
Write-Host "triage_matrix_ready  : $($summary.review_finding_triage_matrix_ready)"
Write-Host "remediation_packet   : $($summary.remediation_plan_packet_ready)"
Write-Host "closure_gate_ready   : $($summary.remediation_closure_gate_ready)"
Write-Host "real_approvals       : $($summary.real_remediation_approval_count)"
Write-Host "closed_findings      : $($summary.review_finding_closed_count)"
Write-Host "external_review_ready: $($summary.real_external_review_ready)"
Write-Host "external_pilot_ready : $($summary.real_external_pilot_ready)"
Write-Host "production_ready     : $($summary.production_ready)"
Write-Host "full_biosdk_ready    : $($summary.full_biosdk_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.external_review_finding_triage_contract_ready) {
    throw "v5.53 external review finding triage contract failed"
}
if ($summary.real_remediation_approval_count -ne 0) {
    throw "v5.53 must not claim real remediation approvals"
}
if ($summary.review_finding_closed_count -ne 0) {
    throw "v5.53 must not claim closed review findings"
}
if ($summary.real_external_review_ready) {
    throw "v5.53 must not claim real external review readiness"
}
if ($summary.real_external_pilot_ready) {
    throw "v5.53 must not claim real external pilot readiness"
}
if ($summary.production_ready) {
    throw "v5.53 must not claim production readiness"
}
if ($summary.full_biosdk_ready) {
    throw "v5.53 must not claim full BioSDK readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.53 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v553 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v553_external_review_finding_triage.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.53 External Review Finding Triage Contract PASSED"
Write-Host "====================================================="
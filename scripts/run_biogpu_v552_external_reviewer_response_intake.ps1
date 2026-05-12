param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v552_external_reviewer_response_intake"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.52  External Reviewer Response Intake"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v552 external reviewer response intake proof ---"
& $Python -m biogpu.benchmarks.biogpu_v552_external_reviewer_response_intake --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- External reviewer response intake summary ---"
$summaryPath = Join-Path $OutDir "V552_EXTERNAL_REVIEWER_RESPONSE_INTAKE_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "contract_ready       : $($summary.external_reviewer_response_intake_contract_ready)"
Write-Host "v551_dependency      : $($summary.v551_dependency_ready)"
Write-Host "scoring_matrix_ready : $($summary.questionnaire_scoring_matrix_ready)"
Write-Host "response_packet_ready: $($summary.signed_review_response_packet_ready)"
Write-Host "response_gate_ready  : $($summary.signed_review_response_gate_ready)"
Write-Host "signed_responses     : $($summary.signed_review_response_ready_count)"
Write-Host "external_reviews     : $($summary.external_review_completed_count)"
Write-Host "external_review_ready: $($summary.real_external_review_ready)"
Write-Host "external_pilot_ready : $($summary.real_external_pilot_ready)"
Write-Host "production_ready     : $($summary.production_ready)"
Write-Host "full_biosdk_ready    : $($summary.full_biosdk_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.external_reviewer_response_intake_contract_ready) {
    throw "v5.52 external reviewer response intake contract failed"
}
if ($summary.signed_review_response_ready_count -ne 0) {
    throw "v5.52 must not claim real signed review responses"
}
if ($summary.external_review_completed_count -ne 0) {
    throw "v5.52 must not claim completed external reviews"
}
if ($summary.real_external_review_ready) {
    throw "v5.52 must not claim real external review readiness"
}
if ($summary.real_external_pilot_ready) {
    throw "v5.52 must not claim real external pilot readiness"
}
if ($summary.production_ready) {
    throw "v5.52 must not claim production readiness"
}
if ($summary.full_biosdk_ready) {
    throw "v5.52 must not claim full BioSDK readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.52 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v552 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v552_external_reviewer_response_intake.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.52 External Reviewer Response Intake Contract PASSED"
Write-Host "====================================================="
param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v556_external_signoff_transcript_intake"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.56  External Signoff Transcript Intake"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v556 external signoff transcript intake proof ---"
& $Python -m biogpu.benchmarks.biogpu_v556_external_signoff_transcript_intake --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- External signoff transcript intake summary ---"
$summaryPath = Join-Path $OutDir "V556_EXTERNAL_SIGNOFF_TRANSCRIPT_INTAKE_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status        : $($summary.overall_status)"
Write-Host "contract_ready        : $($summary.external_signoff_transcript_intake_contract_ready)"
Write-Host "v555_dependency       : $($summary.v555_dependency_ready)"
Write-Host "intake_matrix         : $($summary.external_signoff_intake_matrix_ready)"
Write-Host "transcript_packet     : $($summary.signed_closure_transcript_packet_ready)"
Write-Host "acceptance_gate       : $($summary.transcript_acceptance_gate_ready)"
Write-Host "real_signoffs_accepted: $($summary.real_external_signoff_accepted_count)"
Write-Host "transcripts_accepted  : $($summary.signed_closure_transcript_accepted_count)"
Write-Host "closed_findings       : $($summary.review_finding_closed_count)"
Write-Host "production_distance   : $($summary.production_distance_assessment.distance)"
Write-Host "bic_os_distance       : $($summary.bic_os_distance_assessment.distance)"
Write-Host "external_review_ready : $($summary.real_external_review_ready)"
Write-Host "external_pilot_ready  : $($summary.real_external_pilot_ready)"
Write-Host "production_ready      : $($summary.production_ready)"
Write-Host "full_biosdk_ready     : $($summary.full_biosdk_ready)"
Write-Host "bic_os_phase_locked   : $($summary.bic_os_phase_locked)"

if (-not $summary.external_signoff_transcript_intake_contract_ready) {
    throw "v5.56 external signoff transcript intake contract failed"
}
if ($summary.real_external_signoff_accepted_count -ne 0) {
    throw "v5.56 must not accept real external signoffs"
}
if ($summary.signed_closure_transcript_accepted_count -ne 0) {
    throw "v5.56 must not accept signed closure transcripts"
}
if ($summary.review_finding_closed_count -ne 0) {
    throw "v5.56 must not claim closed review findings"
}
if ($summary.real_external_signoff_intake_ready) {
    throw "v5.56 must not claim real external signoff intake readiness"
}
if ($summary.real_external_signoff_accepted) {
    throw "v5.56 must not claim accepted real external signoffs"
}
if ($summary.signed_closure_transcript_accepted) {
    throw "v5.56 must not claim accepted signed closure transcripts"
}
if ($summary.real_external_review_ready) {
    throw "v5.56 must not claim real external review readiness"
}
if ($summary.real_external_pilot_ready) {
    throw "v5.56 must not claim real external pilot readiness"
}
if ($summary.production_ready) {
    throw "v5.56 must not claim production readiness"
}
if ($summary.full_biosdk_ready) {
    throw "v5.56 must not claim full BioSDK readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.56 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v556 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v556_external_signoff_transcript_intake.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.56 External Signoff Transcript Intake Contract PASSED"
Write-Host "====================================================="
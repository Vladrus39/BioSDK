param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v555_closure_signoff_registry"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.55  Closure Signoff Registry"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v555 closure signoff registry proof ---"
& $Python -m biogpu.benchmarks.biogpu_v555_closure_signoff_registry --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Closure signoff registry summary ---"
$summaryPath = Join-Path $OutDir "V555_CLOSURE_SIGNOFF_REGISTRY_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "contract_ready       : $($summary.closure_signoff_registry_contract_ready)"
Write-Host "v554_dependency      : $($summary.v554_dependency_ready)"
Write-Host "registry_matrix      : $($summary.signoff_registry_matrix_ready)"
Write-Host "audit_trail_ready    : $($summary.closure_signoff_audit_trail_ready)"
Write-Host "signoff_packet       : $($summary.external_reviewer_signoff_packet_ready)"
Write-Host "real_reviewer_signoff: $($summary.real_external_reviewer_signoff_ready_count)"
Write-Host "real_closure_signoff : $($summary.real_closure_signoff_ready_count)"
Write-Host "closed_findings      : $($summary.review_finding_closed_count)"
Write-Host "production_distance  : $($summary.production_distance_assessment.distance)"
Write-Host "bic_os_distance      : $($summary.bic_os_distance_assessment.distance)"
Write-Host "external_review_ready: $($summary.real_external_review_ready)"
Write-Host "external_pilot_ready : $($summary.real_external_pilot_ready)"
Write-Host "production_ready     : $($summary.production_ready)"
Write-Host "full_biosdk_ready    : $($summary.full_biosdk_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.closure_signoff_registry_contract_ready) {
    throw "v5.55 closure signoff registry contract failed"
}
if ($summary.real_external_reviewer_signoff_ready_count -ne 0) {
    throw "v5.55 must not claim real external reviewer signoffs"
}
if ($summary.real_closure_signoff_ready_count -ne 0) {
    throw "v5.55 must not claim real closure signoffs"
}
if ($summary.review_finding_closed_count -ne 0) {
    throw "v5.55 must not claim closed review findings"
}
if ($summary.real_external_review_ready) {
    throw "v5.55 must not claim real external review readiness"
}
if ($summary.real_external_pilot_ready) {
    throw "v5.55 must not claim real external pilot readiness"
}
if ($summary.production_ready) {
    throw "v5.55 must not claim production readiness"
}
if ($summary.full_biosdk_ready) {
    throw "v5.55 must not claim full BioSDK readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.55 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v555 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v555_closure_signoff_registry.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.55 Closure Signoff Registry Contract PASSED"
Write-Host "====================================================="
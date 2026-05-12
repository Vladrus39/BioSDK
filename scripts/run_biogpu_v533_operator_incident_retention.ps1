param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v533_operator_incident_retention"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.33  Operator Incident Retention"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v533 operator incident retention proof ---"
& $Python -m biogpu.benchmarks.biogpu_v533_operator_incident_retention --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Operator incident retention summary ---"
$summaryPath = Join-Path $OutDir "V533_OPERATOR_INCIDENT_RETENTION_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "incident_ready       : $($summary.operator_incident_retention_ready)"
Write-Host "acknowledgement      : $($summary.operator_acknowledgement_ready)"
Write-Host "resolution           : $($summary.incident_resolution_ready)"
Write-Host "retention_manifest   : $($summary.incident_retention_manifest_ready)"
Write-Host "audit_bundle         : $($summary.incident_audit_bundle_ready)"
Write-Host "production_retention : $($summary.production_incident_retention_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.operator_incident_retention_ready) {
    throw "v5.33 operator incident retention proof failed"
}
if ($summary.production_operator_workflow_ready) {
    throw "v5.33 must not claim production operator workflow readiness"
}
if ($summary.production_incident_retention_ready) {
    throw "v5.33 must not claim production incident retention readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.33 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v533 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v533_operator_incident_retention.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.33 Operator Incident Retention PASSED"
Write-Host "====================================================="
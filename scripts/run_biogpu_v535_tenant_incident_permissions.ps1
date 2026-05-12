param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v535_tenant_incident_permissions"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.35  Tenant Incident Permissions"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v535 tenant incident permissions proof ---"
& $Python -m biogpu.benchmarks.biogpu_v535_tenant_incident_permissions --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Tenant incident permissions summary ---"
$summaryPath = Join-Path $OutDir "V535_TENANT_INCIDENT_PERMISSIONS_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "permissions_ready    : $($summary.tenant_incident_permissions_ready)"
Write-Host "matrix_ready         : $($summary.permission_matrix_ready)"
Write-Host "tenant_isolation     : $($summary.tenant_isolation_passed)"
Write-Host "viewer_write_denial  : $($summary.viewer_write_denial_passed)"
Write-Host "ledger_scope         : $($summary.ledger_validation_scope_passed)"
Write-Host "production_auth      : $($summary.production_auth_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.tenant_incident_permissions_ready) {
    throw "v5.35 tenant incident permissions proof failed"
}
if ($summary.production_auth_ready) {
    throw "v5.35 must not claim production auth readiness"
}
if ($summary.production_incident_permissions_ready) {
    throw "v5.35 must not claim production incident permissions readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.35 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v535 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v535_tenant_incident_permissions.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.35 Tenant Incident Permissions PASSED"
Write-Host "====================================================="
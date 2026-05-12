param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v536_dashboard_route_contract"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.36  Dashboard Route Contract"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v536 dashboard route-contract proof ---"
& $Python -m biogpu.benchmarks.biogpu_v536_dashboard_route_contract --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Dashboard route-contract summary ---"
$summaryPath = Join-Path $OutDir "V536_DASHBOARD_ROUTE_CONTRACT_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "dashboard_ready      : $($summary.dashboard_route_contract_ready)"
Write-Host "route_count          : $($summary.route_count)"
Write-Host "access_matrix_ready  : $($summary.dashboard_access_matrix_ready)"
Write-Host "viewer_write_denial  : $($summary.viewer_write_denial_passed)"
Write-Host "tenant_isolation     : $($summary.tenant_isolation_passed)"
Write-Host "production_dashboard : $($summary.production_dashboard_ready)"
Write-Host "production_auth      : $($summary.production_auth_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.dashboard_route_contract_ready) {
    throw "v5.36 dashboard route-contract proof failed"
}
if ($summary.production_dashboard_ready) {
    throw "v5.36 must not claim production dashboard readiness"
}
if ($summary.production_auth_ready) {
    throw "v5.36 must not claim production auth readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.36 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v536 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v536_dashboard_route_contract.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.36 Dashboard Route Contract PASSED"
Write-Host "====================================================="
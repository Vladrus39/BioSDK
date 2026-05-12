param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v528_authenticated_local_service"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.28  Authenticated Local Service"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v528 authenticated local service proof ---"
& $Python -m biogpu.benchmarks.biogpu_v528_authenticated_local_service --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Authenticated local service summary ---"
$summaryPath = Join-Path $OutDir "V528_AUTHENTICATED_LOCAL_SERVICE_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status        : $($summary.overall_status)"
Write-Host "service_ready         : $($summary.authenticated_local_service_ready)"
Write-Host "api_routes            : $($summary.api_route_count)"
Write-Host "auth_required_for_v1  : $($summary.auth_required_for_v1)"
Write-Host "scope_denial_passed   : $($summary.scope_denial_passed)"
Write-Host "download_contract     : $($summary.result_bundle_download_contract_passed)"
Write-Host "production_api_ready  : $($summary.production_api_ready)"
Write-Host "bic_os_phase_locked   : $($summary.bic_os_phase_locked)"

if (-not $summary.authenticated_local_service_ready) {
    throw "v5.28 authenticated local service proof failed"
}
if ($summary.production_api_ready) {
    throw "v5.28 must not claim production API readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.28 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v528 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v528_authenticated_local_service.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.28 Authenticated Local Service PASSED"
Write-Host "====================================================="
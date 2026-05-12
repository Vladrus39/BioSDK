param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v537_identity_provider_contract"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.37  Identity Provider Contract"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v537 identity-provider contract proof ---"
& $Python -m biogpu.benchmarks.biogpu_v537_identity_provider_contract --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Identity-provider contract summary ---"
$summaryPath = Join-Path $OutDir "V537_IDENTITY_PROVIDER_CONTRACT_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "identity_ready       : $($summary.identity_provider_contract_ready)"
Write-Host "oidc_contract        : $($summary.oidc_discovery_contract_ready)"
Write-Host "jwks_contract        : $($summary.jwks_rotation_contract_ready)"
Write-Host "validation_matrix    : $($summary.identity_validation_matrix_ready)"
Write-Host "dashboard_access     : $($summary.identity_dashboard_access_ready)"
Write-Host "production_auth      : $($summary.production_auth_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.identity_provider_contract_ready) {
    throw "v5.37 identity-provider contract proof failed"
}
if ($summary.production_auth_ready) {
    throw "v5.37 must not claim production auth readiness"
}
if ($summary.production_identity_ready) {
    throw "v5.37 must not claim production identity readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.37 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v537 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v537_identity_provider_contract.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.37 Identity Provider Contract PASSED"
Write-Host "====================================================="
param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v546_private_registry_auth_feed"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.46  Private Registry Auth Feed"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v546 private registry auth/feed proof ---"
& $Python -m biogpu.benchmarks.biogpu_v546_private_registry_auth_feed --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Private registry auth/feed summary ---"
$summaryPath = Join-Path $OutDir "V546_PRIVATE_REGISTRY_AUTH_FEED_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "contract_ready       : $($summary.private_registry_auth_feed_contract_ready)"
Write-Host "v545_dependency      : $($summary.v545_dependency_ready)"
Write-Host "auth_feed_matrix     : $($summary.auth_feed_matrix_ready)"
Write-Host "feed_manifest        : $($summary.expiring_feed_manifest_ready)"
Write-Host "expiry_probe         : $($summary.expiring_feed_probe_ready)"
Write-Host "registry_log_export  : $($summary.registry_log_export_contract_ready)"
Write-Host "real_registry_auth   : $($summary.real_private_registry_auth_ready)"
Write-Host "live_registry        : $($summary.live_private_registry_ready)"
Write-Host "full_biosdk_ready    : $($summary.full_biosdk_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.private_registry_auth_feed_contract_ready) {
    throw "v5.46 private registry auth/feed contract failed"
}
if ($summary.real_private_registry_auth_ready) {
    throw "v5.46 must not claim real private registry auth readiness"
}
if ($summary.live_private_registry_ready) {
    throw "v5.46 must not claim live private registry readiness"
}
if ($summary.full_biosdk_ready) {
    throw "v5.46 must not claim full BioSDK readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.46 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v546 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v546_private_registry_auth_feed.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.46 Private Registry Auth Feed Contract PASSED"
Write-Host "====================================================="
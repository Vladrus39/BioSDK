param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v547_registry_revoke_yank_notification"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.47  Registry Revoke/Yank Notification"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v547 registry revoke/yank notification proof ---"
& $Python -m biogpu.benchmarks.biogpu_v547_registry_revoke_yank_notification --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Registry revoke/yank notification summary ---"
$summaryPath = Join-Path $OutDir "V547_REGISTRY_REVOKE_YANK_NOTIFICATION_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "contract_ready       : $($summary.registry_revoke_yank_notification_contract_ready)"
Write-Host "v546_dependency      : $($summary.v546_dependency_ready)"
Write-Host "matrix_ready         : $($summary.revoke_yank_matrix_ready)"
Write-Host "yank_manifest        : $($summary.local_yank_manifest_ready)"
Write-Host "notification_trail   : $($summary.recipient_notification_ack_trail_ready)"
Write-Host "effect_probe         : $($summary.revoke_yank_effect_probe_ready)"
Write-Host "incident_linkage     : $($summary.incident_linkage_export_ready)"
Write-Host "production_yank      : $($summary.production_yank_ready)"
Write-Host "live_registry        : $($summary.live_private_registry_ready)"
Write-Host "full_biosdk_ready    : $($summary.full_biosdk_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.registry_revoke_yank_notification_contract_ready) {
    throw "v5.47 registry revoke/yank notification contract failed"
}
if ($summary.production_yank_ready) {
    throw "v5.47 must not claim production yank readiness"
}
if ($summary.live_private_registry_ready) {
    throw "v5.47 must not claim live private registry readiness"
}
if ($summary.full_biosdk_ready) {
    throw "v5.47 must not claim full BioSDK readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.47 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v547 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v547_registry_revoke_yank_notification.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.47 Registry Revoke/Yank Notification Contract PASSED"
Write-Host "====================================================="
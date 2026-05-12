param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v531_recovery_alerting"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.31  Recovery Alerting"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v531 recovery alerting proof ---"
& $Python -m biogpu.benchmarks.biogpu_v531_recovery_alerting --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Recovery alerting summary ---"
$summaryPath = Join-Path $OutDir "V531_RECOVERY_ALERTING_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "recovery_ready       : $($summary.recovery_alerting_ready)"
Write-Host "stale_alert          : $($summary.stale_heartbeat_alert_passed)"
Write-Host "failure_classified   : $($summary.failure_classification_passed)"
Write-Host "worker_recovery      : $($summary.worker_recovery_passed)"
Write-Host "audit_bundle         : $($summary.recovery_audit_bundle_ready)"
Write-Host "production_recovery  : $($summary.production_recovery_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.recovery_alerting_ready) {
    throw "v5.31 recovery alerting proof failed"
}
if ($summary.production_recovery_ready) {
    throw "v5.31 must not claim production recovery readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.31 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v531 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v531_recovery_alerting.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.31 Recovery Alerting PASSED"
Write-Host "====================================================="
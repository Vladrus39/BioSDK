param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v545_recipient_onboarding_audit"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.45  Recipient Onboarding Audit"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v545 recipient onboarding audit proof ---"
& $Python -m biogpu.benchmarks.biogpu_v545_recipient_onboarding_audit --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Recipient onboarding audit summary ---"
$summaryPath = Join-Path $OutDir "V545_RECIPIENT_ONBOARDING_AUDIT_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "contract_ready       : $($summary.recipient_onboarding_audit_contract_ready)"
Write-Host "v544_dependency      : $($summary.v544_dependency_ready)"
Write-Host "onboarding_matrix    : $($summary.recipient_onboarding_matrix_ready)"
Write-Host "access_log           : $($summary.recipient_access_log_ready)"
Write-Host "expiry_probe         : $($summary.access_expiry_probe_ready)"
Write-Host "real_onboarding      : $($summary.real_recipient_onboarding_ready)"
Write-Host "live_registry        : $($summary.live_private_registry_ready)"
Write-Host "full_biosdk_ready    : $($summary.full_biosdk_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.recipient_onboarding_audit_contract_ready) {
    throw "v5.45 recipient onboarding audit contract failed"
}
if ($summary.real_recipient_onboarding_ready) {
    throw "v5.45 must not claim real recipient onboarding readiness"
}
if ($summary.live_private_registry_ready) {
    throw "v5.45 must not claim live private registry readiness"
}
if ($summary.full_biosdk_ready) {
    throw "v5.45 must not claim full BioSDK readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.45 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v545 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v545_recipient_onboarding_audit.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.45 Recipient Onboarding Audit Contract PASSED"
Write-Host "====================================================="
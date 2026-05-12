param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v540_private_beta_onboarding_contract"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.40  Private Beta Onboarding Contract"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v540 private beta onboarding proof ---"
& $Python -m biogpu.benchmarks.biogpu_v540_private_beta_onboarding --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Private beta onboarding summary ---"
$summaryPath = Join-Path $OutDir "V540_PRIVATE_BETA_ONBOARDING_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "onboarding_ready     : $($summary.private_beta_onboarding_contract_ready)"
Write-Host "v539_dependency      : $($summary.v539_dependency_ready)"
Write-Host "release_operations   : $($summary.release_operations_contract_ready)"
Write-Host "participant_gate     : $($summary.participant_gate_ready)"
Write-Host "external_beta_ready  : $($summary.external_beta_ready)"
Write-Host "full_biosdk_ready    : $($summary.full_biosdk_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.private_beta_onboarding_contract_ready) {
    throw "v5.40 private beta onboarding contract failed"
}
if ($summary.external_beta_ready) {
    throw "v5.40 must not claim external beta readiness"
}
if ($summary.full_biosdk_ready) {
    throw "v5.40 must not claim full BioSDK readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.40 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v540 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v540_private_beta_onboarding.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.40 Private Beta Onboarding Contract PASSED"
Write-Host "====================================================="
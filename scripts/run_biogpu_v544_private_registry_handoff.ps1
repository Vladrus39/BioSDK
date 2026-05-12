param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v544_private_registry_handoff"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.44  Private Registry Handoff"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v544 private registry handoff proof ---"
& $Python -m biogpu.benchmarks.biogpu_v544_private_registry_handoff --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Private registry handoff summary ---"
$summaryPath = Join-Path $OutDir "V544_PRIVATE_REGISTRY_HANDOFF_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "contract_ready       : $($summary.private_registry_handoff_contract_ready)"
Write-Host "v543_dependency      : $($summary.v543_dependency_ready)"
Write-Host "local_handoff        : $($summary.local_handoff_package_ready)"
Write-Host "access_matrix        : $($summary.handoff_access_matrix_ready)"
Write-Host "revocation_probe     : $($summary.handoff_revocation_probe_ready)"
Write-Host "registry_index       : $($summary.local_registry_index_ready)"
Write-Host "live_registry        : $($summary.live_private_registry_ready)"
Write-Host "full_biosdk_ready    : $($summary.full_biosdk_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.private_registry_handoff_contract_ready) {
    throw "v5.44 private registry handoff contract failed"
}
if (-not $summary.local_handoff_package_ready) {
    throw "v5.44 local handoff package did not pass"
}
if ($summary.live_private_registry_ready) {
    throw "v5.44 must not claim live private registry readiness"
}
if ($summary.full_biosdk_ready) {
    throw "v5.44 must not claim full BioSDK readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.44 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v544 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v544_private_registry_handoff.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.44 Private Registry Handoff Contract PASSED"
Write-Host "====================================================="
param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v539_packaged_sdk_install_gate"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.39  Packaged SDK Install Gate"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v539 packaged SDK install gate proof ---"
& $Python -m biogpu.benchmarks.biogpu_v539_packaged_sdk_install_gate --root . --out-dir $OutDir --build-distribution --require-wheel-build

Write-Host ""
Write-Host "--- Packaged SDK install gate summary ---"
$summaryPath = Join-Path $OutDir "V539_PACKAGED_SDK_INSTALL_GATE_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "install_gate_ready   : $($summary.packaged_sdk_install_gate_ready)"
Write-Host "metadata_contract    : $($summary.package_metadata_contract_ready)"
Write-Host "entrypoint_contract  : $($summary.entrypoint_contract_ready)"
Write-Host "wheel_build          : $($summary.local_wheel_build_ready)"
Write-Host "install_smoke        : $($summary.local_install_smoke_ready)"
Write-Host "full_biosdk_ready    : $($summary.full_biosdk_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.packaged_sdk_install_gate_ready) {
    throw "v5.39 packaged SDK install gate failed"
}
if (-not $summary.local_wheel_build_ready) {
    throw "v5.39 local wheel build did not pass"
}
if (-not $summary.local_install_smoke_ready) {
    throw "v5.39 local install smoke did not pass"
}
if ($summary.full_biosdk_ready) {
    throw "v5.39 must not claim full BioSDK readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.39 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v539 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v539_packaged_sdk_install_gate.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.39 Packaged SDK Install Gate PASSED"
Write-Host "====================================================="
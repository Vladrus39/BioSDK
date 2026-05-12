param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v541_clean_room_install_report"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.41  Clean-Room Install Report"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v541 clean-room install report proof ---"
& $Python -m biogpu.benchmarks.biogpu_v541_clean_room_install_report --root . --out-dir $OutDir --run-local-install-probe --require-local-install-probe

Write-Host ""
Write-Host "--- Clean-room install report summary ---"
$summaryPath = Join-Path $OutDir "V541_CLEAN_ROOM_INSTALL_REPORT_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "contract_ready       : $($summary.clean_room_install_report_contract_ready)"
Write-Host "v540_dependency      : $($summary.v540_dependency_ready)"
Write-Host "environment_contract : $($summary.environment_contract_ready)"
Write-Host "report_completeness  : $($summary.report_completeness_ready)"
Write-Host "local_install_probe  : $($summary.local_clean_room_install_probe_ready)"
Write-Host "external_report      : $($summary.external_clean_room_report_ready)"
Write-Host "full_biosdk_ready    : $($summary.full_biosdk_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.clean_room_install_report_contract_ready) {
    throw "v5.41 clean-room install report contract failed"
}
if (-not $summary.local_clean_room_install_probe_ready) {
    throw "v5.41 local clean-room install probe did not pass"
}
if ($summary.external_clean_room_report_ready) {
    throw "v5.41 must not claim external clean-room report readiness"
}
if ($summary.full_biosdk_ready) {
    throw "v5.41 must not claim full BioSDK readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.41 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v541 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v541_clean_room_install_report.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.41 Clean-Room Install Report Contract PASSED"
Write-Host "====================================================="
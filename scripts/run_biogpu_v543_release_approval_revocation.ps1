param(
    [string]$Python = "python",
    [string]$OutDir = "outputs/v543_release_approval_revocation"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "."
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"

Write-Host "====================================================="
Write-Host " BioGPU-Core v5.43  Release Approval and Revocation"
Write-Host "====================================================="
Write-Host "Python: $Python"
Write-Host "Root  : ."
Write-Host "OutDir: $OutDir"
Write-Host ""

Write-Host "--- Running v543 release approval/revocation proof ---"
& $Python -m biogpu.benchmarks.biogpu_v543_release_approval_revocation --root . --out-dir $OutDir

Write-Host ""
Write-Host "--- Release approval/revocation summary ---"
$summaryPath = Join-Path $OutDir "V543_RELEASE_APPROVAL_REVOCATION_SUMMARY.json"
$summary = Get-Content $summaryPath -Raw | ConvertFrom-Json
Write-Host "overall_status       : $($summary.overall_status)"
Write-Host "contract_ready       : $($summary.release_approval_revocation_contract_ready)"
Write-Host "v542_dependency      : $($summary.v542_dependency_ready)"
Write-Host "approval_matrix      : $($summary.release_approval_matrix_ready)"
Write-Host "revocation_drill     : $($summary.release_revocation_drill_ready)"
Write-Host "local_handoff        : $($summary.local_candidate_handoff_approved)"
Write-Host "production_release   : $($summary.production_release_approved)"
Write-Host "full_biosdk_ready    : $($summary.full_biosdk_ready)"
Write-Host "bic_os_phase_locked  : $($summary.bic_os_phase_locked)"

if (-not $summary.release_approval_revocation_contract_ready) {
    throw "v5.43 release approval/revocation contract failed"
}
if (-not $summary.local_candidate_handoff_approved) {
    throw "v5.43 local candidate handoff was not approved"
}
if ($summary.production_release_approved) {
    throw "v5.43 must not approve production release"
}
if ($summary.full_biosdk_ready) {
    throw "v5.43 must not claim full BioSDK readiness"
}
if (-not $summary.bic_os_phase_locked) {
    throw "v5.43 must keep BiC OS phase locked"
}

Write-Host ""
Write-Host "--- Running v543 tests ---"
& $Python -m pytest -q tests/current/test_biogpu_v543_release_approval_revocation.py

Write-Host ""
Write-Host "====================================================="
Write-Host " v5.43 Release Approval and Revocation Contract PASSED"
Write-Host "====================================================="